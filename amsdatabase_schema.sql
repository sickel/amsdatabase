create table system(
    id integer primary key not null IDENTITY(1,1),
    name varchar(255),
    description text,
    addtime datetime default current_timestamp,
    addby varchar(100)
);

create table project(
    id integer primary key not null IDENTITY(1,1),
    name varchar(255),
    training bit not null default 1,
    addtime datetime default current_timestamp,
    addby varchar(100)
);

create table survey(
    id integer primary key not null IDENTITY(1,1),
    startup datetime not null,
    systemid integer not null references system(id),
    projectid integer references project(id),  
    description text,
    addtime datetime default current_timestamp,
    addby varchar(100)
);


create table datafile(
    id integer primary key not null IDENTITY(1,1),
    filename varchar(100) not null,
    md5 varchar(100),
    surveyid integer not null references survey(id),
    addtime datetime default current_timestamp,
    addby varchar(100)
    );

create table measurement(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100),
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
    addby varchar(100),
    systemid integer not null references system(id),
    name varchar(50),
    type varchar(50),
    volumeliter integer    
); 
 
create table detectormeasure(
    id integer primary key not null IDENTITY(1,1),
    addtime datetime default current_timestamp,
    addby varchar(100),
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

