# METARman_japan
## Overview
  **METARman_japan** shows you METAR from almost all of Japanese airport. Their locations are visualized on the map, and you can read their names and their current METAR if you click (on your PC) or tap (on your smartphone) the pin on their locations. His design, structure, and function are very simple that there is no need to worry about struggling or having trouble figuring out how to use him. You do not have to install anything but only visiting the url is enough. 
  url: <https://yamawaking.github.io/METARman_japan/>
  
## Structures and Functions
 ・He imports folium, requests, re, datetime, timezone, random, ThreadPoolExecutor.
 
 ・The icao code of all AIRPORTS he handle are below:

*RJCC_RJCK_RJCW_RJCA_RJCO_RJSS_RJSU_RJSB_RJSH_RJSK_RJSC_RJSN_RJAA_RJTJ_RJTA_RJTU_RJTC_RJTI_RJNK_RJNS_RJNA_RJME_RJBB_RJBE_RJOA_RJOT_RJOK_RJFF_RJFT_RJFK_RJFY_ROAH_ROMC*

 ・He gets METAR data from NOAA, so if there is no data he cannot show you the METAR data.
 
 ・His colorization rules of the METAR data and the location pins are below:
 
 _wind speed_: If a *GUST* occurs, he colorize it yellow.
 
 _horizontal visibility_: If it is less than 9999, he colorize it blue.
 
 _present weather_: If there is one or more present weather, he colorize them red.
 
 _cloud_: If there is ceiling, he colorize it green.
 
 _location pin_: If you can get the latest METAR, he colorize the pins blue. If you cannot, he colorize them orange (delayed data) or gray (no data).
 
 ・The clock on the page indicates UTC.

 
