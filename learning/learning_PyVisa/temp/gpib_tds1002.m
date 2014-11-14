%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%FILE: gpib_tds210.m  
%CREATED 27 April 2004      BY Robert Nyman
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%To download data from a Tektronix TDS210 Oscilloscope, with minimal effort
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%03-06-04 Modified for use with TDS1002 oscilloscope XXXXXX
%

clear, format short g, format compact

g=gpib('mcc',0,1);
fopen(g);

%fprintf(g,'*IDN?');temp=fscanf(g);temp

disp('Querying Oscilloscope for parameters')
fprintf(g,'DATA:ENC ASCII');%Sets format for data transfer
fprintf(g,'DATA:WIDTH 1');%Sets vertical quantization to XXXXXXX 2 bytes(16 bits)XXXXXXXXXXXXXXXXXXX
fprintf(g,'DATA:STOP 2500');

%Set buffer size large enough to receive all the data in one go
fprintf(g,'DATA:START?');temp=fscanf(g,'%s');
Nstart=str2num(temp(1:size(temp,2)));
fprintf(g,'DATA:STOP?');temp=fscanf(g,'%s');
Nstop=str2num(temp(1:size(temp,2)));

%Query oscilloscope for display parameters
fprintf(g,'WFMPRE:XINCR?');temp=fscanf(g);
x_incr=str2num(temp(1:size(temp,2)));%horizontal, usually in seconds per point

Narbitrary=50;
Npts_temp=8*(Nstop-Nstart+1)-6+Narbitrary;Npts_temp=Npts_temp*4;
fclose(g);set(g,'InputBufferSize',Npts_temp);fopen(g)

disp('Downloading CH1 Data')
fprintf(g,'DATA:SOURCE CH1');%Sets source for data
fprintf(g,'WFMPRE:YMULT?');temp=fscanf(g);
y_incr_ch1=str2num(temp(14:size(temp,2)));%vertical scale, in Volts per unit
fprintf(g,'CURVE?');temp=fscanf(g,'%s',Npts_temp);
ch1_temp=temp;Npts_ch1temp=size(ch1_temp,2);
temp2=temp(7:Npts_ch1temp);
temp3=str2num(temp2);
ch1_data=temp3;

disp('Downloading CH2 Data')
fprintf(g,'DATA:SOURCE CH2');%Sets source for data
fprintf(g,'WFMPRE:YMULT?');temp=fscanf(g);
y_incr_ch2=str2num(temp(14:size(temp,2)));%vertical scale, in Volts per unit
fprintf(g,'CURVE?');temp=fscanf(g,'%s',Npts_temp);temp;
ch2_temp=temp;Npts_ch2temp=size(ch2_temp,2);
temp2=temp(7:Npts_ch2temp);
temp3=str2num(temp2);
ch2_data=temp3;

disp('Postprocessing')
t=x_incr*(Nstart:Nstop);
x1=ch1_data*y_incr_ch1;
x2=ch2_data*y_incr_ch2;

plot(1000*t,x1,1000*t,x2)
xlabel('Time / ms')
ylabel('Signal / Volts')
grid on

%break
fclose(g);
delete(g);
%instrfind

%File output
fnam='E:\Manip\2004_06\sat_abs\temp-xx.dat';
output=[t' x1' x2'];
save(fnam,'output','-ascii')

%End of File