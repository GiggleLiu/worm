'''
Initialize databases.
'''
from models import init_tables,init_sources

if __name__=='__main__':
    init_tables()
    init_sources()
