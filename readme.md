# Tutorial (venv) de instalação Biuri Landing:

1. [Instalação e configuração do apache](https://hackmd.io/zq0I9AdhSMun4Z8upmU27A#Instala%C3%A7%C3%A3o-e-configura%C3%A7%C3%A3o-do-apache)
2. [Download do repositório para servidor](https://hackmd.io/zq0I9AdhSMun4Z8upmU27A#Dowload-do-reposit%C3%B3rio-para-servidor)
3. [Instalação das dependências](https://hackmd.io/zq0I9AdhSMun4Z8upmU27A#Instala%C3%A7%C3%A3o-das-depend%C3%AAncias)
4. [Configurando SSL com o Let's Encrypt]()


## Instalação e configuração do apache

- Referência: https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-18-04-pt

Primeiro vamos atualizar os pacotes do sistema:

```
sudo apt update
```

Vamos instalar o apache2

```
sudo apt install apache2
```

No final do processo de instalação, o Ubuntu 18.04 inicia o Apache. O servidor Web já deve estar em funcionamento.

Verifique com o sistema init ```systemd``` para garantir que o serviço está funcionando digitando:

```
sudo systemctl status apache2
```

```
# saída

● apache2.service - The Apache HTTP Server
   Loaded: loaded (/lib/systemd/system/apache2.service; enabled; vendor preset: enabled)
  Drop-In: /lib/systemd/system/apache2.service.d
           └─apache2-systemd.conf
   Active: active (running) since Tue 2018-04-24 20:14:39 UTC; 9min ago
 Main PID: 2583 (apache2)
    Tasks: 55 (limit: 1153)
   CGroup: /system.slice/apache2.service
           ├─2583 /usr/sbin/apache2 -k start
           ├─2585 /usr/sbin/apache2 -k start
           └─2586 /usr/sbin/apache2 -k start
```

Agora podemos entrar no browser e verificar se a instalção e o serviço apache está funcionando:

```http://198.74.62.126```

Configurando arquivo padrão de configuração do servidor apache2:

```
nano /etc/apache2/sites-available/000-default.conf
```

Ao abrir o arquivo ```000-default.conf``` copie e cole a seguinte configuração:

```
<VirtualHost *:80>
        ServerAdmin oda@member.fsf.org
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        ServerName biuri.wemind.com.br

        ProxyPreserveHost On
        ProxyPass / http://127.0.0.1:8080/
        ProxyPassReverse / http://127.0.0.1:8080/

        RewriteEngine on
        # RewriteCond %{SERVER_NAME} =biuri.wemind.com.br
        RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

Como editamos o arquivo padrão de configuração após salva-lo ele já estará habilitado por padrão. Recomenda-se que em casos de configuração de mais de 1 domínio você crie novos arquivos invés de editar o arquivo padrão, isso facilitará na organização do seu servidor.

Ao criar um novo arquivo ele não estará habilitado por padrão, para isso você poderá utilizar a ferramenta ```a2ensite``` para habilitá-lo. Siga um tutorial para isso [aqui](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-18-04-pt#passo-5-%E2%80%94-configurando-hosts-virtuais-(recomendado)).


## Dowload do repositório para servidor

Primeiramente vamos instalar o git:

```
sudo apt install git
```

Na home ou no diretório do seu usuário crie uma pasta para o projeto:

```
mkdir biuri-landing
```

Agora entre na pasta e dê um ```git init```:

```
cd biuri-landing
git init
```

Configure o repositório web como origem:

```
git remote add origin https://bitbucket.org/biuri/biuri-landing/src/master/
```

Agora vamos baixar o repositório para o servidor:

```
git clone https://bitbucket.org/biuri/biuri-landing/src/master/
```

Vá até o master e confira quais são os pacotes que faltam no arquivo ```base.txt```:

```
nano /biuri-landing/master/requirements/base.txt
```

## Instalação das dependências

Agora vamos instalar o python3.6 ao lado do 3.8:

```
add-apt-repository ppa:deadsnakes/ppa
apt-get update
apt-get install python3.6
```


Em seguida instalamos o pip3:

```
sudo apt install pip3
```

Especifique que a instalação dos pacotes será feita com o python3.6:

```
python3.6 -m pip install -r requirements.txt
```

Depois de instalar todas as dependências é preciso criar o banco de dados mysql, para isso digite o comando que abrirá a interface MYSQL:

- Referência: https://www.mysqltutorial.org/mysql-create-database/

```
mysql -u root -p
```
saída
```
mysql> 'digite o comando aqui'
```

Agora vamos criar o banco de dados de nossa aplicação com o comando:

```
CREATE DATABASE biuri
```

Você pode conferir seus bancos de dados Mysql com o comando:

```
SHOW DATABASES;
```

Com o banco de dados criado temos fazer uma migração do nosso DB com os seguintes comandos:

```
python manage.py makemigrations
python manage.py migrate
```

Feito isso podemos fazer o servidor rodar:

```
python manage.py runserver
```

## Configurando SSL com o Let's Encrypt

[![Tutorial de instalação gratuira de Let's Encrypt com a ferramenta CertBot](https://i.ytimg.com/an_webp/d-FQ0JTfUxI/mqdefault_6s.webp?du=3000&sqp=CPyJiIAG&rs=AOn4CLBpVqKo_q3K_28zMpbZN_Mck68fNA)](https://www.youtube.com/watch?v=d-FQ0JTfUxI)
> Tutorial de instalação gratuira de Let's Encrypt com a ferramenta CertBot

Agora vamos utilizar a ferramenta [CertBot](https://certbot.eff.org/) para instalar e configurar gratuitamente um SSL em nosso domínio.
