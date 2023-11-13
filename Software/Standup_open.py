import webbrowser

device_list = ["A19F","A17E","A3EB","A505","A316","A30A","A23B","A451","A529","A4A5","A4CC"]
urls = []
for id in device_list:
        url = "http://standup-" + id + ".local:5000/"
        urls.append(url)
        print(url)

# open urls in browser
for url in urls:
    webbrowser.open(url, new=2)