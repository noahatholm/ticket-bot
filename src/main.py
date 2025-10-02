from ticket_bot import TicketBot

import os


def main():
    #ragger = Rag("..//rag//images", "..//corpus//")
    # for chunk in ragger.get_chunks():
    #     print("##############################")
    #     print(chunk.to_json())
    #print(ragger.query("'The router can work as an access point, transforming your existing wired network to awireless one.1.\tVisithttp://tplinkwifi.net, and log in with your TP-Link ID or the password you set forthe router.2.\tGo toAdvanced>System>Operation Mode, selectAccess PointModeand clickSAVE. The router will reboot and switch to Access Point mode.18Chapter 4Set Up Internet Connection3.\tAfter rebooting, connect the router to your existing wired router via an Ethernet cable.4."))
    os.system("Ticket Suppot Bot")


    json_path = "..//inputs.json"
    bot = TicketBot(json_path)
    print("Starting Discord Bot")
    bot.run_bot()


if __name__ == "__main__":
    main()