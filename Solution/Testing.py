from TypeTools import run_pipeline
from Grammar import get_grammar

G, _, _, _, _, _, _ = get_grammar()

text = '''
class A {
    a : int ;
    suma ( a : int , b : int ) : int {
        a + b 
    };
    b : int ;
};
'''

if __name__ == '__main__':
    run_pipeline(G, text)
    #assert not errors

text = '''
class A {
    a : int ;
    suma ( a : int , b : int ) : int {
        a + b + new B 
    };
    b : int ;
};
'''

if __name__ == '__main__':
    run_pipeline(G, text)
    """
    assert set(errors) == {
	 'Operation is not defined between "int" and "B".',
	 'Cannot convert "int" into "A".'
    }
    """