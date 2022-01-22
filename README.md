# Hello!
> If you ever need help join my [server](https://discord.com/invite/ChS8MZDPRA)

## Cogs:
- [OTTSX](https://github.com/B1tterSw33t/BitterSweet-Cogs#ottsx)
- [EmbedSpeaker](https://github.com/B1tterSw33t/BitterSweet-Cogs#embedspeaker)
- [RCL](https://github.com/B1tterSw33t/BitterSweet-Cogs#rcl)


## OTTSX
> Searching 1337x

Basicaly a dupe of the nyaa cog, but redone for 1337x.
I plan on expanding this to do some other features, but for now it's a start.

### Commands
- `ottsx lookup <query>`
    - Search for a torrent

### Todo
- [ ] Detect links in chat and give information

## EMBEDSPEAKER
> Messages to Embeds

Simple tool to convert messages into embeds the moment they're sent.

### Commands
- `embedspeaker add`
    - Enable the channel the command was sent in.
- `embedspeaker remove`
    - Disable the channel the command was sent in.
### Todo
- [ ] `embedspeaker embedstyle`
    - Customize how the embed looks.
- [ ] Support channel mentions for add/remove.

## RCL
> Rclone fronted for discord

### Commands
> Spaces in filepaths (yes even with quotes) do not work currently for some reason.
- `rcl listremotes`
- `rcl raw <stuff>`
    - Anything put after this is the same as running an rclone command in cosole
    > Careful running data managment commands, it can be taxing on your vps
- `rcl lsf <remote_path>`
    
- `rcl config`
    - `rcl config add`
        - Add a remote, you copy paste this front he rclone config file.
    - `rcl config remove`
        - Removes a remote from the saved config
    - `rcl config reset`
        - Deletes all saved remotes, there's no confirmation message.

### Todo
- honestly to long to make a list, the features are any that are not related to data transfer for now since I don't want to destroy my vps and cost myself a lot of money... Maybe I should settup a donation feaute? I like money.