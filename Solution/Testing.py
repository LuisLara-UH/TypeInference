from TypeTools import run_pipeline
from Grammar import get_grammar

G, _, _, _, _, _, _ = get_grammar()

text = '''
class Main inherits IO { 
    main ( ) : AUTO_TYPE
    {
        let x : AUTO_TYPE <- 3 in 
            case x of
                y : Int => out_string ( " OK " ) ;
            esac
    } ;

 } ; 
'''

if __name__ == '__main__':
    run_pipeline(text)
    #assert not errors