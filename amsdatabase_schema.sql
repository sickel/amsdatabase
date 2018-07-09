create table system(
    id integer primary key not null IDENTITY(1,1),
    name varchar(255),
    description text,
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user
);

alter table system add constraint UK_systemname unique (name);

create table project(
    id integer primary key not null IDENTITY(1,1),
    name varchar(255),
    training bit not null default 1,
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user
);

alter table project add constraint UK_projectname unique  (name);

create table survey(
    id integer primary key not null IDENTITY(1,1),
    name varchar(100) not null,
    startup datetime not null,
    systemid integer not null references system(id),
    projectid integer references project(id),  
    description text,
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user
);


create table datafile(
    id integer primary key not null IDENTITY(1,1),
    filename varchar(100) not null,
    md5 varchar(100),
    surveyid integer not null references survey(id),
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user
    );

alter table datafile add constraint UK_datafilename unique  (filename);
    
create table measurement(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user,
    datafileid integer not null references datafile(id),
    SeqNum integer not null,
    systemtime datetime not null,
    aqutimeus integer not null,
    GPSSmplFlags varchar(255) not null,
    GpsError varchar(255) not null,
    GpsTime varchar(255) not null,
    PDOP numeric not null,
    Longitude numeric not null,
    Latitude numeric not null,
    GPSAltitude numeric not null,
    AboveGroundAltitude numeric,
    LineNum numeric,
    adc1 numeric,
    adc2 numeric,
    temp numeric,
    press numeric,
    location geometry 
    );
 
create table detector(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user,
    systemid integer not null references system(id),
    name varchar(50),
    type varchar(50),
    volumeliter integer    
); 
alter table detector add constraint UK_detectorsystem (systemid,name)
 
create table detectormeasure(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100) default current_user,
    name varchar(20),
    ndet integer not null,
    dose numeric,
    totcount numeric,
    spectra varchar(max)
) 
  
 
  
create table calculated(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100),
    detectormeasureid integer references detectormeasure(id),
    item varchar(255) not null, 
    val numeric not null,
    unit varchar(255)
)


create table updatefile(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100),
    filename varchar(100) not null,
    md5 varchar(100)
)



insert into system(name,description) values('330-1','4x4 liter RS-500');
insert into system(name,description) values('330-2','4x4 liter RS-500');
insert into system(name,description) values('NGU','5x4 liter RS-500');
insert into system(name,description) values('NRPA-25l','5x4 liter RS-500');
insert into system(name,description) values('NRPA-Østerås','RS-701');
insert into system(name,description) values('NRPA-Svanhovd','RS-701');

insert into detector(systemid,name,type,volumeliter) (select id,'Total','NaI',16 from system where name='330-1');

insert into detector(systemid,name,type,volumeliter) (select id,'Total','NaI',8 from system where name='NRPA-Østerås');
insert into detector(systemid,name,type,volumeliter) (select id,'Left','NaI',4 from system where name='NRPA-Østerås');
insert into detector(systemid,name,type,volumeliter) (select id,'Right','NaI',4 from system where name='NRPA-Østerås');
insert into detector(systemid,name,type,volumeliter) (select id,'3"','NaI',1 from system where name='NRPA-Østerås');
insert into detector(systemid,name,type,volumeliter) (select id,'Nøytron','Nøytron',0 from system where name='NRPA-Østerås');
insert into detector(systemid,name,type,volumeliter) (select id,'Total','NaI',16 from system where name='330-2');
insert into detector(systemid,name,type,volumeliter) (select id,'Total','NaI',8 from system where name='NRPA-Svanhovd');
insert into detector(systemid,name,type,volumeliter) (select id,'Left','NaI',4 from system where name='NRPA-Svanhovd');
insert into detector(systemid,name,type,volumeliter) (select id,'Right','NaI',4 from system where name='NRPA-Svanhovd');
insert into detector(systemid,name,type,volumeliter) (select id,'Down','NaI',4 from system where name='NRPA-25l');
insert into detector(systemid,name,type,volumeliter) (select id,'Up','NaI',4 from system where name='NRPA-25l');
insert into detector(systemid,name,type,volumeliter) (select id,'Down','NaI',4 from system where name='NGU');
insert into detector(systemid,name,type,volumeliter) (select id,'Up','NaI',4 from system where name='NGU');
