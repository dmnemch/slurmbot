import subprocess
import time
import telebot
import yaml

config = yaml.load("~/.config/slurmbot/config.yaml")

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
    return messages, flag

def run_bot(jobs, token, chat, mode, sleep_time):
    telebot.TeleBot(token).send_message(chat_id=chat, text=f"Bot is running in {mode} mode with {sleep_time}s latency")
    _ = get_finished_jobs(jobs)
    messages = []
    old_flag = False
    if mode == 'batch':
        while True:
            new_messages, new_flag = get_finished_jobs(jobs)
            print(new_messages)    
            messages += new_messages
            if not new_flag and old_flag:
                send_message(messages, token, chat)
                messages = []
            old_flag = new_flag
            time.sleep(sleep_time)
    elif mode == 'single':
        while True:
            messages, new_flag = get_finished_jobs(jobs)
            send_message(messages, token, chat)
            time.sleep(sleep_time)
def main():
    run_bot(jobs = {}, token=config['token'], chat=config['token'], mode=config['mode'], sleep_time=config['sleep_time'])

if __name__ == '__main__':
    main()
