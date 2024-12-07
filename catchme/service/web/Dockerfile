FROM httpd:2.4.50

COPY ./conf/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./conf/extra/httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
COPY ./conf/www.catch.me.key /usr/local/apache2/conf/www.catch.me.key
COPY ./conf/www.catch.me.crt /usr/local/apache2/conf/www.catch.me.crt
COPY ./conf/intranet.catch.me.key /usr/local/apache2/conf/intranet.catch.me.key
COPY ./conf/intranet.catch.me.crt /usr/local/apache2/conf/intranet.catch.me.crt

RUN mkdir /usr/local/apache2/htdocs/www/
RUN chmod 755 /usr/local/apache2/htdocs/www/
COPY ./www/index.html /usr/local/apache2/htdocs/www/index.html

RUN mkdir /usr/local/apache2/htdocs/intranet/
RUN chmod 755 /usr/local/apache2/htdocs/intranet/
COPY ./intranet/index.html /usr/local/apache2/htdocs/intranet/index.html

RUN mkdir /usr/local/apache2/htdocs/intranet-old/
RUN chmod 755 /usr/local/apache2/htdocs/intranet-old/
COPY ./intranet-old/index.html /usr/local/apache2/htdocs/intranet-old/index.html
COPY ./intranet-old/.htaccess /usr/local/apache2/htdocs/intranet-old/.htaccess
COPY ./intranet-old/.htpasswd /usr/local/apache2/htdocs/intranet-old/.htpasswd

#CMD ["httpd-foreground"]