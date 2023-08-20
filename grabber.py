import tkinter as tk
import praw
import json
import requests
import re
import os
import threading


class RedditMediaDownloader(tk.Tk):
    def __init__(self):
        """Initialize the GUI for our Reddit Image Grabber. All the goodness begins here!"""
        tk.Tk.__init__(self)
        self.title("Reddit Image Grabber")
        self.geometry("400x600")
        self.configure(bg="#2E2E2E")

        # Fonts for headers and labels.
        header_font = ("Arial", 12, "underline")
        label_font = ("Arial", 10)

        # Function to create labels, 'cause I like doing it this way.
        def create_label(text, font=None, fg="#FFFFFF"):
            return tk.Label(self, text=text, font=font, fg=fg, bg="#2E2E2E")

        # Load previous credentials if available.
        self.cred_path = "credentials.json"
        if os.path.exists(self.cred_path):
            with open(self.cred_path) as f:
                cred = json.load(f)
        else:
            cred = {}

        # Reddit credentials section:
        create_label("Reddit Credentials", font=header_font).pack(pady=5)
        create_label("Client ID:", font=label_font).pack()
        self.client_id_entry = tk.Entry(self)
        self.client_id_entry.insert(0, cred.get('client_id', ''))
        self.client_id_entry.pack(pady=2)
        create_label("Client Secret:", font=label_font).pack()
        self.client_secret_entry = tk.Entry(self, show="*")
        self.client_secret_entry.insert(0, cred.get('client_secret', ''))
        self.client_secret_entry.pack(pady=2)
        create_label("Password:", font=label_font).pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.insert(0, cred.get('password', ''))
        self.password_entry.pack(pady=2)
        create_label("Username:", font=label_font).pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.insert(0, cred.get('username', ''))
        self.username_entry.pack(pady=2)
        create_label("User Agent:", font=label_font).pack()
        self.user_agent_entry = tk.Entry(self)
        self.user_agent_entry.insert(0, cred.get('user_agent', ''))
        self.user_agent_entry.pack(pady=2)

        # Subreddit and Options section:
        create_label("Subreddit:", font=header_font).pack(pady=5)
        self.subreddit_entry = tk.Entry(self)
        self.subreddit_entry.pack(pady=2)
        create_label("Options:", font=header_font).pack(pady=5)
        create_label("Sort by:", font=label_font).pack()
        self.sort_var = tk.StringVar(self)
        self.sort_var.set("top")
        self.sort_menu = tk.OptionMenu(self, self.sort_var, "top", "new", "hot", "rising")
        self.sort_menu.config(bg="#2E2E2E", fg="#FFFFFF")
        self.sort_menu.pack(pady=2)
        create_label("Limit:", font=label_font).pack()
        self.limit_entry = tk.Entry(self)
        self.limit_entry.pack(pady=2)
        create_label("Time Filter:", font=label_font).pack()
        self.when_var = tk.StringVar(self)
        self.when_var.set("all")
        self.when_menu = tk.OptionMenu(self, self.when_var, "all", "year", "month", "week", "day", "hour")
        self.when_menu.config(bg="#2E2E2E", fg="#FFFFFF")
        self.when_menu.pack(pady=2)

        # Files download status label.
        self.downloaded_label = create_label("Files downloaded: 0", font=label_font)
        self.downloaded_label.pack(pady=5)

        # Buttons to start and stop the download.
        self.button_frame = tk.Frame(self, bg="#2E2E2E")
        self.button_frame.pack(pady=10)
        self.start_button = tk.Button(self.button_frame, text="Start Download", command=self.start_download_thread)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(self.button_frame, text="Stop Download", command=self.stop_download, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # A thread for the download task and a flag to handle stopping it. This is on a separate thread so we can keep the GUI responding to count images, stop download, etc.
        self.download_thread = None
        self.stop_download_flag = False

    def start_download_thread(self):
        """Starts the download in a separate thread, 'cause we don't want our GUI to freeze."""
        self.download_thread = threading.Thread(target=self.start_download)
        self.download_thread.start()
        self.stop_button.config(state=tk.NORMAL)
        self.downloaded_label.config(fg="yellow")

    def stop_download(self):
        """A big red stop button (figuratively speaking) to stop the download."""
        self.stop_download_flag = True

    def start_download(self):
        """Gather the info from the form, dump it to the json, and initiate the download process."""
        cred = {
            "client_id": self.client_id_entry.get(),
            "client_secret": self.client_secret_entry.get(),
            "password": self.password_entry.get(),
            "username": self.username_entry.get(),
            "user_agent": self.user_agent_entry.get()
        }
        subreddit = self.subreddit_entry.get()
        sort = self.sort_var.get()
        limit = int(self.limit_entry.get())
        when = self.when_var.get()

        with open(self.cred_path, 'w') as f:
            json.dump(cred, f)

        reddit = praw.Reddit(**cred)

        self.download_images(reddit, subreddit, sort=sort, limit=limit, when=when)

    def download_images(self, reddit, sub, sort='top', limit=300, when='all'):
        """Download images from the specified subreddit."""
        downloaded_count = 0
        if not os.path.exists(sub):
            os.mkdir(sub)
        subreddit = reddit.subreddit(sub)
        gen = getattr(subreddit, sort)(when, limit=limit)
        url_pattern = re.compile(r'https://(external-)?preview\.redd\.it/(?P<name>.+\.(?:jpg|png))')

        # Loop through the posts and download the images.
        for i in gen:
            if self.stop_download_flag:
                break
            if not i.is_self:
                att = dir(i)
                if 'is_gallery' in att and i.gallery_data:
                    image_ids = [x['media_id'] for x in i.gallery_data['items']]
                    for x in image_ids:
                        images = i.media_metadata[x]['p']
                        if images:
                            url = max(images, key=lambda y: y['y'])['u']
                            img = requests.get(url).content
                            match = url_pattern.search(url)
                            if match:
                                name = match.group('name')
                                with open(sub + '/' + name, 'wb') as f:
                                    f.write(img)
                                downloaded_count += 1
                elif 'preview' in att and i.preview['images']:
                    url = i.preview['images'][0]['source']['url']
                    img = requests.get(url).content
                    match = url_pattern.search(url)
                    if match:
                        name = match.group('name')
                        with open(sub + '/' + name, 'wb') as f:
                            f.write(img)
                        downloaded_count += 1

            self.downloaded_label.config(text=f"Files downloaded: {downloaded_count}")

        # Reset the stop flag and update the label color to original.
        self.stop_download_flag = False
        self.downloaded_label.config(fg="#FFFFFF")
        self.stop_button.config(state=tk.DISABLED)


app = RedditMediaDownloader()
app.mainloop()
