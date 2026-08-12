# 🏷️ NFC Smart Chore Tracker

A lightweight, local, and physical chore-tracking system powered by a Raspberry Pi, Flask, NFC tags, and `ntfy.sh`. 

Instead of relying on nagging or opening an app to check off a list, simply tap your phone against a physical NFC tag placed where the chore happens (e.g., the litterbox or the dishwasher). The system automatically tracks whose turn it is, sends morning reminders to the assigned person, and broadcasts a celebratory push notification to the household when the chore is done.

## ✨ Features
* **Physical Interactions:** Log chores by tapping an NFC tag with your smartphone.
* **Smart Accountability:** Uses 10-year browser cookies to permanently identify which household member tapped the tag.
* **Strict Turn Enforcement:** Prevents someone from logging a chore if it isn't their turn.
* **Automatic Rotation:** A daily cron job automatically rotates chores to the next person once completed.
* **Targeted Notifications:** Uses [ntfy.sh](https://ntfy.sh) to send morning assignments *only* to the person whose turn it is. 
* **Global Celebrations:** Broadcasts a "Chore Complete!" push notification to the whole house so nobody repeats the work.

## 🛠️ Hardware Requirements
* **Raspberry Pi:** (A Raspberry Pi Zero W is perfect).
* **NFC Tags:** NTAG215 or similar blank stickers.
* **Smartphones:** Any NFC-enabled Android or iPhone (e.g., Google Pixel).

## 💻 Software Prerequisites
* Python 3.x
* Flask (`pip install Flask`)
* Requests (`pip install requests`)
* GNU `screen` (for running the Flask server in the background)
* The [ntfy](https://ntfy.sh/) app installed on your phones.
