Simple telegram bot to notify slurm job is done.

1. Install via `pip install slurmbot`
2. Make an empty config file via `mkdir -p ~/.config/slurmbot && touch ~/.config/slurmbot/config.yaml`
3. Make your telegram bot with BotFather, paste token into config file (like in example.yaml)
4. Get your chat id with @RawDataBot, paste it into config file (like in example.yaml)
5. Add `slurmbot &` to your ~/.bashrc or ~/.zshrc file
