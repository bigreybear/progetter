from src.NobelDealer import NobelDealer
from src.TuringDealer import TuringDealer

if __name__ == '__main__':
    ndd = TuringDealer()
    ndd.rebuild("url_turing.bin")
    ndd.collect_personal_info()