from TypeTools import run_pipeline
from Grammar import get_grammar

G, _, _, _, _, _, _ = get_grammar()

text = '''
class A inherits B { 
    F ( n : AUTO_TYPE ) : AUTO_TYPE
    {
        if n <= 2 then self else F ( n - 1 ) fi
    } ;

 } ; 
 class B
 {
     a : A ;
     G ( n : AUTO_TYPE , p : AUTO_TYPE ) : AUTO_TYPE
     {
         a . F ( n )
     } ;
 }    ;
'''

if __name__ == '__main__':
    run_pipeline(G, text)
    #assert not errors