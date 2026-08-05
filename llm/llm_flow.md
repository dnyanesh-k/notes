# LLM Internals — Complete Theory (Interview Reference)

## Table of Contents
1. [Overview](#1-overview)
2. [Tokenization](#2-tokenization)
3. [Tensors](#3-tensors)
4. [Embeddings](#4-embeddings)
5. [Positional Embeddings](#5-positional-embeddings)
6. [Input Representation](#6-input-representation)
7. [Self-Attention Mechanism](#7-self-attention-mechanism)
8. [Query, Key, Value Vectors](#8-query-key-value-vectors)
9. [Attention Scores](#9-attention-scores)
10. [Scaling](#10-scaling)
11. [Causal Attention Mask](#11-causal-attention-mask)
12. [Softmax in Attention](#12-softmax-in-attention)
13. [Weighted Sum of Values](#13-weighted-sum-of-values)
14. [Multi-Head Attention](#14-multi-head-attention)
15. [Residual Connections](#15-residual-connections)
16. [Layer Normalization](#16-layer-normalization)
17. [Feed Forward Network](#17-feed-forward-network)
18. [Repeated Layers (Stacking Transformer Blocks)](#18-repeated-layers-stacking-transformer-blocks)
19. [Final Hidden Vector](#19-final-hidden-vector)
20. [Logits](#20-logits)
21. [Softmax and Probability Distribution](#21-softmax-and-probability-distribution)
22. [Next Token Prediction Strategies](#22-next-token-prediction-strategies)
23. [Autoregressive Generation](#23-autoregressive-generation)
24. [Training: Loss Function](#24-training-loss-function)
25. [Backpropagation](#25-backpropagation)
26. [Gradients](#26-gradients)
27. [Optimizer](#27-optimizer)
28. [Iterations and Learning](#28-iterations-and-learning)
29. [End-to-End Flow Summary](#29-end-to-end-flow-summary)
30. [Quick Interview Q&A Reference](#30-quick-interview-qa-reference)

---

## 1. Overview

A Large Language Model (LLM) is a neural network, almost always based on the Transformer architecture, that is trained to predict the next token in a sequence of text. Despite the apparent complexity of models with billions of parameters, the underlying pipeline is a fixed sequence of well-defined stages: raw text is converted into tokens, tokens are converted into numeric IDs, IDs are converted into vectors (embeddings), those vectors are enriched with positional information, and then passed through a stack of Transformer blocks that use self-attention and feed-forward networks to build contextual understanding. The final output is a probability distribution over the vocabulary, from which the next token is sampled. This document walks through every stage of that pipeline in the same order it happens inside the model, followed by how the model is trained to get good at this task in the first place.

**Key Points:**
- LLM = neural network trained to predict the next token.
- Almost all modern LLMs are built on the Transformer architecture.
- Pipeline order: text → tokens → token IDs → embeddings → positional info → Transformer stack → logits → probabilities → next token.
- Two separate concerns to keep distinct in an interview: inference (how a trained model generates text) versus training (how the model's weights are learned).

## 2. Tokenization

Tokenization is the first step in the pipeline and converts raw human-readable text into smaller units called tokens. A tokenizer does not necessarily split text into whole words; it commonly splits into sub-word units so that both common words and rare words, misspellings, or unseen words can still be represented using a fixed vocabulary. For example, the sentence "The cat sat on mat" can be tokenized into whole words as `["The", "cat", "sat", "on", "mat"]`, while a sub-word tokenizer might break a word like "The" into fragments such as `["Th", "e"]` when the word is uncommon or when byte-pair encoding merges do not cover it as a single unit. Each unique token in the tokenizer's vocabulary is assigned a fixed integer identifier, called a token ID. Continuing the example, the tokens `["The", "cat", "sat", "on", "mat"]` might map to token IDs `[45, 891, 1204, 67, 900]`. This mapping is static and is decided during tokenizer training, long before the language model itself is trained. Tokenization matters for interviews because it explains why LLMs sometimes struggle with character-level tasks (like counting letters) — the model never actually sees individual characters, it sees token IDs.

## 3. Tensors

Deep learning frameworks do not operate on plain lists of numbers; they operate on tensors, which are multi-dimensional arrays optimized for parallel computation on GPUs. A 1-dimensional tensor is just a vector, such as `tensor([45, 891, 1204, 67, 900])` representing the token IDs from the previous step. A 2-dimensional tensor could represent a batch of sequences, and a 3-dimensional tensor could add the embedding dimension on top of that. Every input, weight, and intermediate value inside an LLM is represented as a tensor. The reason tensors matter is computational: matrix and tensor operations can be massively parallelized on GPU hardware, which is what makes training and running models with billions of parameters feasible at all.

## 4. Embeddings

Once text has been converted into token IDs, those IDs must be converted into dense numeric vectors that carry meaning, because raw integer IDs carry no semantic information — token ID 45 is not "closer" to token ID 46 in any meaningful sense. This conversion happens through an embedding lookup, where each token ID indexes into a large learned matrix called the embedding layer. This matrix has one row per vocabulary entry, and each row is a vector of a fixed size (commonly a few hundred to a few thousand dimensions, depending on model size). For example, token ID 45 ("The") might map to an embedding vector like `[0.2, 0.1, 0.7, ...]`, token ID 891 ("cat") might map to `[0.9, 0.3, 0.2, ...]`, and token ID 1204 ("sat") might map to `[0.1, 0.8, 0.4, ...]`. The key idea is that a vector is just a list of numbers, but in machine learning that list represents meaning or features of the token, and tokens with similar meaning end up with similar vectors after training. This embedding matrix is not fixed or hand-designed; its values are learned parameters that get updated during training, just like every other weight in the model.

## 5. Positional Embeddings

Transformers process all tokens in a sequence in parallel rather than one at a time in order, which means the architecture has no built-in sense of word order — the model does not naturally understand which token came first, second, or last. To fix this, a positional embedding is added to each token's embedding vector. Each position in the sequence (position 0, position 1, position 2, and so on) has its own learned or computed vector, for example position 0 might map to `[0.01, 0.00, 0.02]`, position 1 to `[0.03, 0.01, 0.01]`, and position 2 to `[0.05, 0.02, 0.00]`. These positional vectors are pulled from a position embedding structure the same way token embeddings are pulled from the token embedding layer.

## 6. Input Representation

The final input representation for each token is computed by element-wise adding its token embedding vector and its positional embedding vector: `Token Id → Embedding Vector + Positional Embedding`. Concretely, for the token "The" with token ID 45 at position 0, the token embedding `[0.2, 0.1, 0.7]` is added to the positional embedding `[0.01, 0.00, 0.02]` to produce the final input vector `[0.21, 0.10, 0.72]`. The same happens for every token in the sequence: "cat" (ID 891, position 1) combines its embedding with the position-1 vector to get `[0.93, 0.31, 0.21]`, and "sat" (ID 1204, position 2) combines to get `[0.15, 0.82, 0.40]`. These combined vectors are what actually enters the Transformer's attention layers — they simultaneously encode what the token is and where it sits in the sequence.

## 7. Self-Attention Mechanism

Self-attention is the core mechanism that allows a Transformer to build contextual meaning. The intuitive idea is that each token asks a question: "which other tokens are important for understanding me?" For example, in the sentence "The cat sat on the mat," the token "sat" needs to know that "cat" is the one performing the action, so attention allows "sat" to look at and weigh information from "cat" (and every other token) when forming its own contextual representation. This is what allows the model to resolve things like pronoun references, subject-verb relationships, and long-range dependencies across a sentence or document.

## 8. Query, Key, Value Vectors

To perform self-attention, the model does not use the raw input vectors directly. Instead, from every input vector, the model creates three separate vectors: a Query vector, a Key vector, and a Value vector. These are produced using learned weight matrices: `Q = X * Wq`, `K = X * Wk`, `V = X * Wv`, where X is the input embedding (token embedding + positional embedding) and Wq, Wk, Wv are learned weight matrices — the actual trainable knowledge inside the model, sometimes numbering in the billions of parameters (for example, a "7B" model refers to seven billion such learned numbers). Intuitively, the Query represents "what am I looking for," the Key represents "what do I contain that others could match against," and the Value represents "what information do I actually carry if someone attends to me." For the worked example with tokens "The," "cat," "sat," the Query, Key, and Value matrices might look like:
```
Q = [[1,0,1], [1,1,0], [0,1,1]]   # The, cat, sat
K = [[1,1,0], [0,1,1], [1,0,1]]   # The, cat, sat
V = [[10,0], [0,10], [5,5]]       # The, cat, sat
```

## 9. Attention Scores

Once Q, K, and V exist, the model computes attention scores by comparing each token's Query vector against every token's Key vector, using the dot product: `Score = Q . K`. This is often written as `QK^T` (Query multiplied by the transpose of Key), producing a raw similarity score between every pair of tokens. A higher score means a stronger relationship between the two tokens. Continuing the worked example, if we take the Query vector for "sat," `Q_sat = [0, 1, 1]`, and compute its dot product against the Key vectors for "The" `[1,1,0]`, "cat" `[0,1,1]`, and "sat" `[1,0,1]`, we get raw scores of `[1, 2, 1]` respectively. These raw numbers are also referred to interchangeably as attention scores, raw scores, similarity scores, or logits at this stage of the computation.

## 10. Scaling

Raw attention scores are scaled down before being passed through softmax, to keep the values in a numerically stable range and prevent the softmax function from producing extremely peaked (near one-hot) distributions when the dimensionality is large. The scaling factor is the square root of the dimension of the key vectors, written `SQRT(d_k)`, where `d_k` is the dimension of the key vector — in the toy example `d_k = 3`, but in real models it is commonly 64 or 128. So the raw score vector `[1, 2, 1]` gets divided by `SQRT(3) ≈ 1.73`, producing scaled scores of approximately `[0.58, 1.15, 0.58]`. This full operation is captured in the canonical attention formula: `Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V`.

## 11. Causal Attention Mask

In autoregressive language models (models that generate text left to right, one token at a time), a token must not be allowed to attend to tokens that come after it in the sequence, because at generation time those future tokens don't exist yet. To enforce this during training, a causal attention mask is applied to the scaled attention scores before softmax: positions corresponding to future tokens are set to negative infinity so that after softmax they receive a probability of essentially zero. In the worked example, before the mask is applied the score row for "cat" might look like `[1, 4, 2]`, but after the mask is applied (blocking "cat" from attending to future token "sat") it becomes `[1, 4, -∞]`, guaranteeing the softmax output assigns zero weight to the disallowed future position.

## 12. Softmax in Attention

After scaling and masking, the resulting scores are converted into probabilities using the softmax function, so that the scores for each token sum to 1 and behave like a probability distribution over "how much attention to pay to each other token." In this context softmax's output is also called normalized attention weights or attention probabilities. Applying softmax to the scaled scores `[0.58, 1.15, 0.58]` for "sat" produces normalized attention weights of approximately `[0.26, 0.48, 0.26]`, meaning roughly 26% attention to "The," 48% attention to "cat," and 26% attention to itself, "sat." This matches the intuitive expectation that "sat" attends most strongly to "cat," since "cat" is the subject performing the action of sitting — this is often summarized as the model implicitly learning "who sat? → cat."

## 13. Weighted Sum of Values

The final step of a single attention operation is to multiply each token's attention weights by the corresponding Value vectors and sum the results, producing a weighted sum of Values. This is the step that actually mixes information across tokens rather than just scoring relationships. Using the attention weights `[0.26, 0.48, 0.26]` for "sat" and the Value vectors `V = [[10,0], [0,10], [5,5]]` for "The," "cat," "sat" respectively, the weighted sum is computed as `0.26×[10,0] + 0.48×[0,10] + 0.26×[5,5]`, which works out to approximately `[3.9, 6.1]`. This resulting vector is the new, context-aware representation of the token "sat" — it now contains a blend of information from "The," "cat," and itself, weighted by relevance.

## 14. Multi-Head Attention

Rather than performing a single attention operation, Transformer models use multiple attention "heads" in parallel — this is called multi-head attention. Instead of computing one set of Q, K, V projections, the model computes several independent sets, each with its own learned weight matrices, allowing different heads to specialize in different types of relationships. For instance, one head might learn to track grammatical structure, another might specialize in long-range dependencies, and another might capture semantic similarity. The outputs of all heads are concatenated and combined, producing what is referred to as the contextual representation of each token — a vector that now encodes syntax, semantics, context, and relationships to other tokens simultaneously.

## 15. Residual Connections

After the attention sub-layer (and later, after the feed-forward sub-layer), the Transformer adds the original input back to the output of that sub-layer — this is called a residual connection, expressed as `output = new_output + old_input`. Residual connections serve two critical purposes: they help gradients flow backward through very deep networks during training without vanishing, and they ensure that the original information from the input is never fully lost or overwritten as it passes through many stacked layers.

## 16. Layer Normalization

Layer normalization is applied to stabilize the values flowing through the network, typically applied either before or after each sub-layer (attention or feed-forward), depending on the specific architecture variant. Without normalization, the scale of activations can grow or shrink unpredictably as data passes through many layers, which destabilizes training. Layer normalization rescales the values within each layer so that they maintain a consistent, well-behaved distribution, which in turn helps the model train faster and more reliably.

## 17. Feed Forward Network

After the attention block (with its residual connection and normalization), each token's vector is passed independently through a feed-forward neural network — typically two linear layers with a non-linear activation function such as GELU or ReLU in between. Unlike the attention layer, the feed-forward network processes each token's vector independently rather than mixing information across tokens; its role is to apply additional non-linear transformation and further refine each token's representation after the contextual mixing that attention provided.

## 18. Repeated Layers (Stacking Transformer Blocks)

A single Transformer block consists of: self-attention (with residual connection and normalization) followed by a feed-forward network (with its own residual connection and normalization). Real LLMs stack many of these blocks on top of each other — sometimes dozens or over a hundred layers deep. All of the above operations (attention, scaling, masking, softmax, weighted sum, residual, normalization, feed-forward) repeat identically at every one of these stacked layers, with each layer's output becoming the next layer's input. This repetition is what allows the model to build increasingly abstract and refined representations, layer by layer.

## 19. Final Hidden Vector

After passing through all stacked Transformer layers, each token position has a final hidden vector, which represents everything the model has learned about that token in context — including its syntax, its semantics, its relationships to other tokens, and any relevant world knowledge encoded in the model's weights. This is the vector that gets used to actually predict the next token.

## 20. Logits

To go from a final hidden vector to an actual prediction over the vocabulary, the final hidden vector is passed through one more linear layer that projects it into a vector with one entry per vocabulary token — this output is called logits. For a vocabulary of 50,000 tokens, this produces a vector such as `[0.25, ..., <50000 values total>]`, where each value is a raw, unnormalized score representing how strongly the model favors that particular vocabulary token as the next token.

## 21. Softmax and Probability Distribution

The logits are converted into an actual probability distribution using softmax again, this time over the entire vocabulary rather than over attention positions. This produces a probability for every token in the vocabulary, summing to 1. For example, given three candidate next tokens "the," "cat," and "sat," a softmax output of `[0.05, 0.95, 0]` would mean the model assigns 5% probability to "the," 95% probability to "cat," and 0% probability to "sat" as the next token.

## 22. Next Token Prediction Strategies

Once a probability distribution over the vocabulary exists, the model must select one token as its actual output, and there are several common strategies for doing this. Greedy decoding, or `argmax`, always picks the single highest-probability token, which is deterministic but can produce repetitive or bland text. Sampling picks a token randomly according to the probability distribution, introducing variety. Top-k sampling restricts the candidate pool to only the k highest-probability tokens before sampling. Top-p (nucleus) sampling restricts the candidate pool to the smallest set of tokens whose cumulative probability exceeds a threshold p. Temperature sampling adjusts how sharply peaked or flat the probability distribution is before sampling — low temperature makes the model more deterministic and confident, high temperature makes it more random and creative. After a token is selected by any of these strategies, it is converted back from a token ID into readable text.

## 23. Autoregressive Generation

LLMs generate text one token at a time in a loop known as autoregressive generation. After a token is predicted, it is appended back onto the existing input sequence, and the entire process — from embedding lookup through all Transformer layers to next-token prediction — repeats to predict the following token. This continues, one token at a time, until a stopping condition is met, such as generating an end-of-sequence token or reaching a maximum length. This explains why LLMs "type" responses progressively rather than producing the whole answer instantaneously — each token's generation genuinely depends on every token generated before it.

## 24. Training: Loss Function

Everything described so far explains how a trained model produces output; training is the separate process of teaching the model's weights to produce good output in the first place. During training, the model's predicted next token (or more precisely, its predicted probability distribution) is compared against the actual correct next token from the training data, which is called the ground truth — the correct answer is already known because it comes directly from real text. The loss function quantifies how wrong the prediction was: a low loss means the model's prediction was close to the correct answer, while a high loss means it was far off.

## 25. Backpropagation

Once the loss is computed, the model needs to figure out how to adjust its weights to reduce that loss in the future. Backpropagation is the algorithm that makes this possible: the error signal computed at the output is propagated backward through every layer of the network, and for every single weight in the model, backpropagation computes how much that specific weight contributed to the overall error.

## 26. Gradients

The output of backpropagation, for every weight in the model, is a gradient — a value that indicates the direction and magnitude of improvement, essentially answering the question "which weights caused the error, and how should each one change to reduce it?" A gradient can be thought of as a compass pointing in the direction that would most reduce the loss if that specific weight were nudged that way.

## 27. Optimizer

The optimizer is the component responsible for actually updating the model's weights using the computed gradients. Rather than naively subtracting the raw gradient from each weight, modern optimizers (such as Adam, which is extremely common for training LLMs) use more sophisticated update rules that account for momentum and adaptive learning rates, but the core idea remains the same: the optimizer updates weights in the direction that reduces the loss.

## 28. Iterations and Learning

The entire cycle — forward pass through the model to get a prediction, compute loss against ground truth, backpropagate to get gradients, and have the optimizer update the weights — is one training iteration. This cycle is repeated an enormous number of times, often millions or billions of iterations across massive text datasets. Over these repeated iterations, the model gradually and incrementally learns grammar, reasoning patterns, language structure, facts, and coding patterns — not because it was explicitly programmed with any of these, but because minimizing next-token prediction loss across enough real-world text implicitly forces the model to internalize the patterns that make human language and knowledge coherent.

## 29. End-to-End Flow Summary

Putting the entire pipeline together in order: raw text is tokenized into tokens, tokens are converted into token IDs, token IDs are looked up in an embedding matrix to get embedding vectors, positional embeddings are added to encode order, and the resulting input representations enter a stack of Transformer blocks. Inside each block, self-attention computes Query, Key, and Value vectors, calculates attention scores via QK^T, scales them by `sqrt(d_k)`, applies a causal mask to block future tokens, applies softmax to get attention weights, and computes a weighted sum of Value vectors — all done across multiple heads in parallel (multi-head attention) — followed by a residual connection, layer normalization, a feed-forward network, another residual connection, and another layer normalization. This block repeats many times. The final hidden vector from the last layer is projected into logits over the vocabulary, softmax converts logits into a probability distribution, a decoding strategy (argmax, sampling, top-k, top-p, or temperature) selects the next token, and that token is appended back to the sequence for the next generation step — this is autoregressive generation. Separately, during training, this same forward pass is used to compute a loss against the known correct next token, backpropagation computes gradients for every weight, and an optimizer updates all weights accordingly, repeated over massive datasets and enormous numbers of iterations until the model's predictions become reliably accurate.

## 30. Quick Interview Q&A Reference

**Q: Why do LLMs use sub-word tokenization instead of whole words?**
A: It keeps the vocabulary size manageable while still being able to represent rare words, misspellings, and unseen words by breaking them into known sub-word fragments.

**Q: Why are positional embeddings needed if attention already looks at all tokens?**
A: Because self-attention has no inherent notion of order — it treats the sequence as a set unless positional information is explicitly injected into the input vectors.

**Q: What is the purpose of scaling by sqrt(d_k) in attention?**
A: It prevents the dot-product similarity scores from growing too large in magnitude as dimensionality increases, which would otherwise push softmax into an overly peaked, unstable regime.

**Q: Why is a causal mask needed in decoder-only LLMs like GPT?**
A: To prevent a token from attending to future tokens during training, ensuring the model only relies on information that would actually be available at generation time.

**Q: What's the difference between attention weights and the Value vectors they're multiplied against?**
A: Attention weights (from softmax) represent how much to focus on each token; Value vectors represent the actual content/information contributed by each token. The weighted sum combines "how much" with "what."

**Q: Why use multiple attention heads instead of one large attention operation?**
A: Different heads can specialize in capturing different types of relationships (syntax, long-range dependency, semantics) in parallel, giving the model richer representational capacity.

**Q: What do residual connections and layer normalization actually solve?**
A: Residual connections help gradients propagate through very deep networks and preserve original information; layer normalization stabilizes the scale of activations for more reliable training.

**Q: What's the practical difference between temperature, top-k, and top-p sampling?**
A: Temperature reshapes how peaked or flat the whole probability distribution is; top-k restricts sampling to a fixed number of highest-probability tokens; top-p restricts sampling to the smallest set of tokens whose cumulative probability crosses a threshold — all trade off determinism versus diversity in generated text.

**Q: What is a gradient, in plain terms?**
A: A signal, computed per weight via backpropagation, indicating the direction and size of change to that weight that would most reduce the model's prediction error.

**Q: Why does training require so many iterations?**
A: Each iteration only nudges weights slightly based on gradients from one batch of data; broad language capabilities (grammar, reasoning, facts) emerge only after an enormous number of these small, repeated updates across massive and diverse datasets.