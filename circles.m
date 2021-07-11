%%% Non-stationary %%%
clc; clear all; close all
get(0,'Factory');
set(0,'defaultfigurecolor',[1 1 1]);

load circle.csv
load logcircle
T = circle(:,1); X = circle(:,2); Y = circle(:,3); Z = circle(:,4);

T_log = 1:1:length(logcircle(:,1));
Lat_sim = logcircle(:,2); Lon_sim = logcircle(:,3);
PDOP = logcircle(:,6); HDOP = logcircle(:,7); VDOP = logcircle(:,8);
wgs84 = wgs84Ellipsoid('Meter');
[lat_c, lon_c, h_c] = ecef2geodetic(wgs84,X,Y,Z);

downlat = downsample(lat_c,10);
downlon = downsample(lon_c,10);

lat_error_store = zeros(1,length(T_log));
lon_error_store = lat_error_store;
for i=1:length(T_log)
    lat_error = downlat(i) - Lat_sim(i);
    lon_error = downlon(i) - Lon_sim(i);
    lat_error_store(:,i) = lat_error;
    lon_error_store(:,i) = lon_error;
end
lat1 = 69; lon1 = 54.6;
lat_error_sm = lat_error_store.*lat1;
lon_error_sm = lon_error_store.*lon1;
lat_error_meter = sm2km(lat_error_sm)*10^3;
lon_error_meter = sm2km(lon_error_sm)*10^3;

figure(1)
subplot(2,1,1)
plot(T,lat_c)
hold on
plot(T_log, Lat_sim)
title('Latitude value of the circle and simulation')
xlabel('Time [s]')
ylabel('Latitude [$^{\circ}$]', 'Interpreter', 'latex')
legend('Real latitude', 'Simulated latitude')
subplot(2,1,2)
plot(T,lon_c)
hold on
plot(T_log, Lon_sim)
title('Longitude value of the circle and simulation')
xlabel('Time [s]')
ylabel('Longitude [$^{\circ}$]', 'Interpreter', 'latex')
legend('Real longitude', 'Simulated longitude')

figure(2)
plot(T_log,PDOP) 
hold on
plot(T_log,HDOP)
hold on
plot(T_log,VDOP)
hold on
title('DOP values for circle simulation')
xlabel('Time [s]')
ylabel('DOP Value [-]')
legend('PDOP', 'HDOP', 'VDOP')

figure(3)
subplot(2,1,1)
plot(T_log,lat_error_store)
hold on
plot(T_log,lon_error_store)
xlabel('Time [s]')
ylabel('Position error [$^{\circ}$]', 'Interpreter', 'latex')
legend('Latitude position error', 'Longitude position error')
title('Position error of non-stationary simulation')
subplot(2,1,2)
plot(T_log,lat_error_meter)
hold on
plot(T_log,lon_error_meter)
xlabel('Time [s]')
ylabel('Position error [m]')
title('Position error of non-stationary simulation in meters')
legend('Latitude position error', 'Longitude position error')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Other plot options
% subplot(4,1,3)
% plot(T_log,PDOP)
% hold on
% plot(T_log,HDOP)
% hold on
% plot(T_log,VDOP)
% hold on
% title('DOP values for circle simulation')
% xlabel('Time [s]')
% ylabel('DOP Value [-]')
% legend('PDOP', 'HDOP', 'VDOP')
% subplot(4,1,4)
% plot(T_log,lat_error_store)
% hold on
% plot(T_log,lon_error_store)
% xlabel('Time [s]')
% ylabel('Position error [$^{\circ}$]', 'Interpreter', 'latex')
% legend('Latitude position error', 'Longitude position error')
% title('Position error of non-stationary simulation')
% 

% figure(1)
% plot(T,lat_c)
% hold on
% plot(T_log, Lat_sim)
% title('Circle simulation for latitude')
% xlabel('Time [s]')
% ylabel('Latitude [$^{\circ}$]', 'Interpreter', 'latex')
% legend('Real latitude', 'Simulated latitude')
% 
% figure(2)
% plot(T,lon_c)
% hold on
% plot(T_log, Lon_sim)
% title('Circle simulation for longitude')
% xlabel('Time [s]')
% ylabel('Longitude [$^{\circ}$]', 'Interpreter', 'latex')
% legend('Real longitude', 'Simulated longitude')
    