alter table measurement add location_utm geometry;

insert into geometry_columns values('ams','dbo','measurement','location_utm',2,32633,'POINT');