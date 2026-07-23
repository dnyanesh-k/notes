# Two pointer:
**1. is Palindrome LC-125 :**
 -  approach 1 - use `StringBuilder` and create a `newStr`, iterate char-by-char over original string using `s.toCharArray()` and then check if `Character.isLetterOrDigit()` if true then append to `newStr` with `Character.toLowerCase()` and return comparision(`.equals()`) of `newStr.toString()` and `newStr.reverse().toString()`.

 - approach 2 - initialize `left` and `right` pointers pointing to start and end of string, check if `Chracter.isLetterOrDigit()` for value at left and if false then do `left++` and do same for value at right and if false do `right--` and then check compare value at left and right and if doesn't match return `false` else return `true`.

**2. Reverse String LC-344 :** 
- approach 1 - use a `temp` character array, iterate over input array in reverse order and place values from this into `temp` and then re-populate the original array from temp array.

- approach 2 - use a `ArrayList` list and iterate over input char-by-char and `list.add(ch)` values in this list and then  reverse the list `Collections.reverse(list)` and re-populate the original array from this list. 

- approach 3 - initialize a `left` and `right` pointers and iterate till `left < right` and swap `left` and `right` using a `temp` variable.

**3. Two Sum :**
- approach 1 - 