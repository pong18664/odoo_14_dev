FROM odoo:14

USER root
COPY ./requirement.txt /requirement.txt
RUN apt-get update && apt-get install git -y
RUN pip3 install -r requirement.txt
RUN pip3 install html2text
RUN apt install xfonts-thai -y

USER root
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
