import subprocess
import time
import telebot
import yaml
import os

def send_message(messages, token, chat):
    if not messages:
        telebot.TeleBot(token).send_message(chat_id=chat, text='Error: message is empty')
    for i in range(-(-len(messages) // 100)):
        message = "\n".join(messages[i*100:i+1*100])
        telebot.TeleBot(token).send_message(chat_id=chat, text=message, parse_mode='HTML')

def get_finished_jobs(jobs):
    messages = []
    flag = False
    out = subprocess.run('sacct -n --format="jobid,jobname,state,exitcode"', shell=True, capture_output=True).stdout.decode('utf-8').strip().split("\n")
    if out != ['']:
        for line in out:
            job, name, state, err = line.split()
            if "." in job: 
                continue
            if state in ['COMPLETED', 'FAILED']:
                if job not in jobs:
                    message = f"<code>{job}</code> {name + " " if not name == 'None' else ''}{state} with exit code: {err}"
                    messages.append(message)
                    jobs[job] = state
            elif state in ['RUNNING', 'PENDING']:
                flag = True
    else:
        messages = False
    return messages, flag


def run_bot(jobs, token, chat, mode, sleep_time):
    _ = get_finished_jobs(jobs)
    telebot.TeleBot(token).send_message(chat_id=chat, text=f"Bot is running in {mode} mode with {sleep_time}s latency")
    messages = []
    old_flag = False
    if mode == 'batch':
        while True:
            new_messages, new_flag = get_finished_jobs(jobs)
            if new_messages:
                messages += new_messages
                if not new_flag and old_flag:
                    send_message(messages, token, chat)
                    messages = []
                old_flag = new_flag
                time.sleep(sleep_time)
    elif mode == 'single':
        while True:
            messages, new_flag = get_finished_jobs(jobs)
            if new_messages:
                send_message(messages, token, chat)
                time.sleep(sleep_time)

def main():
    path = os.path.expanduser('~/.config/slurmbot/config.yaml')
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    run_bot(jobs = {}, token=config['token'], chat=config['chat'], mode=config['mode'], sleep_time=config['sleep_time'])

if __name__ == '__main__':
    main()
