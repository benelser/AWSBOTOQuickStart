FROM centos:centos7

RUN yum install -y wget cronie gzip gunzip which nmap && yum clean all && rm -rf /var/cache/yum

WORKDIR /work

RUN wget http://download2.rapid7.com/download/InsightVM/Rapid7Setup-Linux64.bin && \
 chmod 755 /work/Rapid7Setup-Linux64.bin && \
 /work/Rapid7Setup-Linux64.bin -q -overwrite -Djava.net.useSystemProxies=false -Vfirstname='NAME' -Vlastname='NAME' -Vcompany='COMPANY' -Vusername='r7user' -Vpassword1='chaNGEmeN0w' -Vpassword2='chaNGEmeN0w' '-Vsys.component.typical$Boolean=true' '-Vsys.component.engine$Boolean=false' '-VcommunicationDirectionChoice$Integer=1' '-VinitService$Boolean=false' && \
 rm -f /work/Rapid7Setup-Linux64.bin

EXPOSE 3780
EXPOSE 40815

COPY license.lic /work/
COPY startR7.sh /startR7
COPY initialize.sh /work/
RUN chmod 755 /work/initialize.sh
RUN chmod 755 /startR7
RUN /work/initialize.sh

CMD ["/startR7"]
