# Kindle Annotations Transfer
A powerful tool to transfer your Kindle highlights to PDF files, making your digital reading experience seamless and organized.

> :memo: **Note:** This project started as a fork of [nsourlos/kindle_to_pdf](https://github.com/nsourlos/kindle_to_pdf).
> It has since diverged significantly.<br>
> Differences:
>
> - Currently, this project specialises in Kindle highlights (without notes) and for the Italian language.
> 

## Quick Installation

You can use venv to create a local Python virtual environment and pip to install the requirements:

### Linux

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Windows

Assicurati di aver impostato l'ambiente ExecutionPolicy adeguata per lo Scope `CurrentUser` tramite il seguente comando eseguito da terminale coi privilegi di amministratore:

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Dunque, esegui i seguenti comandi per creare un ambiente Python in cui installare i file richiesti:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```
