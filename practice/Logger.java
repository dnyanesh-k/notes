// public class Logger{

//     private static final Logger LOGGER = new Logger();

//     private Logger(){};

//     public static Logger getInstance(){
//             return LOGGER;
//     }
// }


public class Logger{

    private static volatile Logger logger;

    private Logger(){};

    public static Logger getInstance(){
        if(logger == null){
            synchronized (Logger.class){
            if(logger == null){    
            logger = new Logger();
            }
          }  
        }
        return logger;
    }
}
