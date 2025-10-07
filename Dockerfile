# FROM odoo:14.0

# USER root
# COPY ./requirement.txt /requirement.txt
# RUN apt-get update && apt-get install git -y
# RUN pip3 install -r requirement.txt
# RUN pip3 install html2text
# RUN apt install xfonts-thai -y
# RUN apt install nano -y

# USER root
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["odoo"]


FROM odoo:14.0

USER root

# สลับไปใช้ mirror ของ archive.debian.org + ปิดการตรวจวันหมดอายุของ repo เก่า
RUN set -eux; \
    sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list; \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list; \
    printf 'Acquire::Check-Valid-Until "false";\nAcquire::AllowInsecureRepositories "true";\n' \
      > /etc/apt/apt.conf.d/99-archive

# ติดตั้งแพ็กเกจระบบที่ต้องใช้ (รวมในบรรทัดเดียวเพื่อตัดปัญหา layer cache)
RUN set -eux; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install -y --no-install-recommends git nano xfonts-thai; \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY ./requirement.txt /requirement.txt
RUN pip3 install -r /requirement.txt && pip3 install html2text

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]

