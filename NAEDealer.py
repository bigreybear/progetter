from NASDealer import NASDealer as NASD
import NASDealer


class NAEDealer(NASD):
    def __init__(self):
        NASD.__init__(self)
        pass

if __name__ == '__main__':
    nae = NAEDealer()
    nae.logger("no")
    # soup = nae.get_soup("https://www.nae.edu/MembersSection/MemberDirectory/30595.aspx")
    soup = nae.get_soup("https://www.nae.edu/MembersSection/MemberDirectory.aspx")
    print soup.prettify()