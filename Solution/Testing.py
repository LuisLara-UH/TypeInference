from TypeTools import run_pipeline
from Grammar import get_grammar

G, _, _, _, _, _, _ = get_grammar()

text = '''
class A {
    a : int ;
    def suma ( a : int , b : int ) : int {
        a + b ;
    }
    b : int ;
}

class B : A {
    c : int ;
    def f ( d : int , a : A ) : void {
        let f : int = 8 ;
        let c = new A ( ) . suma ( 5 , f ) ;
        c ;
    }
}
'''

if __name__ == '__main__':
    ast, errors, context, scope = run_pipeline(G, text)
    assert not errors

text = '''
class A {
    a : int ;
    def suma ( a : int , b : int ) : int {
        a + b + new B ( ) ;
    }
    b : int ;
}

class B : A {
    c : A ;
    def f ( d : int , a : A ) : void {
        let f : int = 8 ;
        let c = new A ( ) . suma ( 5 , f ) ;
        d ;        
    }
}
'''

if __name__ == '__main__':
    ast, errors, context, scope = run_pipeline(G, text)
    assert set(errors) == {
	 'Operation is not defined between "int" and "B".',
	 'Cannot convert "int" into "A".'
    }