# NogizakaBlog
> This project provides an interactive visualization plot of based on Dash and the data were collected from http://blog.nogizaka46.com/
> 
> Further applications are still in progress. 

## Package Version

---
	python == 3.7.9
	re == 2.2.1
	requests == 2.24.0
	bs4 == 4.9.3
	fake_useragent == 0.1.11
	pandas == 1.1.3
	numpy == 1.19.2
	json == 2.0.9
	sqlalchemy == 1.3.20 (database usage)
	dash == 1.17.0

## Execution Process

### Visualization
> **python Visualize_server.py**
> 
> The application will run on 8900 port by default. Interactive interface can be use after connecting to 127.0.0.1:8900.  You should see similar image on your browser. (It is vital to keep the program running while using the application)
![newplot (6)](https://user-images.githubusercontent.com/32337423/99667483-75408600-2aa7-11eb-8003-96342162cdfb.png)
#### args
1. --loadfrom, -l: Load blog data from csv, json or database. Default: "csv"
2. --port, -p: The port the application runs on. Default:8900

You may display the line plot based on various features, generations or combinations of members.
![newplot (5)](https://user-images.githubusercontent.com/32337423/99669936-bb4b1900-2aaa-11eb-996d-262646e86282.png)
![newplot (7)](https://user-images.githubusercontent.com/32337423/99670170-111fc100-2aab-11eb-9141-363309dd59c2.png)

### Crawling
>  **python main.py**
>
> This program will crawl through all the blogs on Nogizaka official blog website and save all the contexts, images and features by default. If you **don't have a mysql database**, you may comment out line 25 and line 35 containing **datamanager.addDataFrametoDataBase** function.

#### args
1. --mode, -m: "init" or "update". If "update" is chosen it will stop crawling after finding the data have already been saved based on date. (Won't update Number of Comments in csv, json and database) Default:"init"

#### features
- Author
- Title
- Date
- Number of Comments
- Number of Characters in Context
- Number of Images
- Context Path
- Generation

## Files
### blogs/
> Where the contexts and images are saved
