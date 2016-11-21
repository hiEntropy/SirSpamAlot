import sys
import Spider


def main():
    args = sys.argv
    argsc = len(args)
    if argsc == 1:
        print(help_menu())
    else:
        profile = check_for('-profile')
        start = check_for('-start')
        if profile and start:
            Spider.spider_pig(start,profile)
        elif profile:
            Spider.spider_pig('car dealers',profile)
        elif start:
            Spider.spider_pig(start,'demographics.json')
        else:
            print(help_menu())
    exit()


def check_for(string):
    return sys.argv[sys.argv.index('-profile')+1] \
        if string in sys.argv and sys.argv.index(string)+1 < len(sys.argv) else None


def help_menu():
    return "-profile denotes a json file that contains details about a person\n" \
           "-start   is a search term, urlencoded, that tells the program where\n" \
           "         to get seed data from. It uses google to get a search\n" \
           "         results page as seed data links."

main()