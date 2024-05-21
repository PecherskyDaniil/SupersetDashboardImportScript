import re
import os
import zipfile
import shutil
import requests
import json
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox

def changedb(filepath,copyfile):
    os.mkdir(filepath.split(".zip")[0])

    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(path=filepath.split(".zip")[0])
    mainpath=filepath.split(".zip")[0]+"/"+os.listdir(filepath.split(".zip")[0])[0]
    file = os.listdir(mainpath+"/databases")[0]
    founddatabaseuuid=re.compile('[\S,\s]+uuid\:\s(.*)\\n')
    foundfakedbuuid=re.compile('[\S,\s]+database_uuid\:\s(.*)\\n')
    f1=open(mainpath+"\\"+"databases\\"+file,"w")
    f2=open(copyfile,"r")
    dbinfo=f2.read()
    dbuuid=founddatabaseuuid.findall(dbinfo)[0]
    f1.write(dbinfo)
    f1.close()
    f2.close()
    for datasetname in os.listdir(mainpath+"/datasets/"+file.split(".")[0]):
        datasetread=open(mainpath.replace("\ "[0],"/")+"/datasets/"+file.split(".")[0]+"/"+datasetname,"r")
        datasetinfo=datasetread.read()
        datasetread.close()
        dataset=open(mainpath+"/datasets/"+file.split(".")[0]+"/"+datasetname,"w")
        dbuuidwrong=foundfakedbuuid.findall(datasetinfo)[0]
        datasetinfo=datasetinfo.replace(dbuuidwrong,dbuuid)
        dataset.write(datasetinfo)
        dataset.close()
    
    os.rename(mainpath+"\\"+"databases\\"+file,mainpath+"\\"+"databases\\"+copyfile.split("/")[-1])
    os.rename(mainpath+"\\"+"datasets\\"+file.split(".")[0],mainpath+"\\"+"datasets\\"+(copyfile.split("/")[-1]).split(".")[0])
    shutil.make_archive((filepath.split("/")[-1]).split(".")[0], 'zip', "./"+(filepath.split("/")[-1]).split(".")[0])
    shutil.rmtree("./"+(filepath.split("/")[-1]).split(".")[0])
def updatedashboard(filepath1,filepath2):
    os.mkdir(filepath1.split(".zip")[0])
    with zipfile.ZipFile( filepath1, 'r') as zip_ref1:
        zip_ref1.extractall(path=filepath1.split(".zip")[0])
    mainpath="./"+(filepath1.split("/")[-1]).split(".")[0]+"/"+os.listdir(filepath1.split(".zip")[0])[0]
    file = os.listdir(mainpath+"/databases")[0]
    founddatabaseuuid=re.compile('[\S,\s]+uuid\:\s(.*)\\n')
    foundfakedbuuid=re.compile('[\S,\s]+database_uuid\:\s(.*)\\n')
    foundslice_id=re.compile('[\S,\s]+slice_id\:\s(.*)\\n')
    os.mkdir(filepath2.split(".zip")[0])
    with zipfile.ZipFile(filepath2, 'r') as zip_ref2:
        zip_ref2.extractall(path=filepath2.split(".zip")[0])
    copypath="./"+(filepath2.split("/")[-1]).split(".")[0]+"/"+os.listdir(filepath2.split(".zip")[0])[0]
    copyfile=copypath+"\\databases\\"+os.listdir(copypath+"/databases")[0]
    f1=open(mainpath+"\\databases\\"+file,"w")
    f2=open(copyfile,"r")
    dbinfo=f2.read()
    dbuuid=founddatabaseuuid.findall(dbinfo)[0]
    f1.write(dbinfo)
    f1.close()
    f2.close()
    for datasetname in os.listdir(mainpath+"/datasets/"+file.split(".")[0]):
        datasetread=open(mainpath.replace("\ "[0],"/")+"/datasets/"+file.split(".")[0]+"/"+datasetname,"r")
        datasetinfo=datasetread.read()
        datasetread.close()
        dataset=open(mainpath+"/datasets/"+file.split(".")[0]+"/"+datasetname,"w")
        dbuuidwrong=foundfakedbuuid.findall(datasetinfo)[0]
        datasetinfo=datasetinfo.replace(dbuuidwrong,dbuuid)
        dataset.write(datasetinfo)
        dataset.close()
    for chartname1 in os.listdir(mainpath+"/charts/"):
        chart1read=open(mainpath.replace("\ "[0],"/")+"/charts/"+chartname1,"r")
        chartinfo=chart1read.read()
        chart1read.close()
        for chartname2 in os.listdir(copypath+"/charts/"):
            if (chartname1.split("_")[0] in chartname2):
                chart2read=open(copypath.replace("\ "[0],"/")+"/charts/"+chartname2,"r")
                if (len(foundslice_id.findall(chart2read.read()))>0):
                    slice_id=foundslice_id.findall(chart2read.read())[0]                
                    chart=open(mainpath+"/charts/"+chartname1,"w")                
                    sliceidwrong=foundslice_id.findall(chartinfo)[0]
                    chartinfo=chartinfo.replace(sliceidwrong,slice_id)
                    chart.write(chartinfo)
                    chart.close()
                chart2read.close()
                
    
    os.rename(mainpath+"\\"+"databases\\"+file,mainpath+"\\"+"databases\\"+copyfile.split(("\ ")[0])[-1])
    os.rename(mainpath+"\\"+"datasets\\"+file.split(".")[0],mainpath+"\\"+"datasets\\"+(copyfile.split(("\ ")[0])[-1]).split(".")[0])
    shutil.make_archive((filepath1.split("/")[-1]).split(".")[0], 'zip', "./"+(filepath1.split("/")[-1]).split(".")[0])
    shutil.rmtree("./"+(filepath1.split("/")[-1]).split(".")[0])
    shutil.rmtree("./"+(filepath2.split("/")[-1]).split(".")[0])
def get_access_token(session,url,password,username):
    api_url=url+"/api/v1/security/login"
    payload = {
      "password": password,
      "provider": "db",
      "refresh": True,
      "username": username
    }
    response = session.post(api_url, json=payload)
    refresh_token = response.json()["refresh_token"]
    access_token = response.json()["access_token"]
    return refresh_token,access_token
def get_csrf_token(session,url,access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    csrf_token=session.get(f"{url}/api/v1/security/csrf_token/",headers=headers).json()
    csrf_token=csrf_token["result"]
    return csrf_token
def get_dashboards_id(access_token,dashboard_name,url,session):
    url = f"{url}/api/v1/dashboard/"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(url, headers=headers)
    dashboard_ids = [dashboard['id']  for dashboard in response.json()['result'] if (dashboard["dashboard_title"]==dashboard_name)]
    if response.status_code == 200:
        return dashboard_ids
    else:
        raise Exception(f"Failed to get dashboard IDs: {response.text}")
def export_dashboards(access_token, dashboard_ids, output_dir,url,session,dashboard_name):
    url = f"{url}/api/v1/dashboard/export/?q={json.dumps(dashboard_ids)}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        zip_file_path = os.path.join(output_dir, dashboard_name+".zip")
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        raise Exception(f"Failed to export dashboards: {response.text}")

def get_database_id(access_token,url,session):
    api_url = f"{url}/api/v1/database/"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(api_url, headers=headers)
    # Формируем список с ids дашбордов
    database_ids = [database['id']  for database in response.json()['result']]
    if response.status_code == 200:
        return database_ids
    else:
        raise Exception(f"Failed to get dashboard IDs: {response.text}")

def export_database(access_token, database_ids, output_dir,url,session):
    api_url = f"{url}/api/v1/database/export/?q={json.dumps(database_ids)}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(api_url, headers=headers, stream=True)
    if response.status_code == 200:
        zip_file_path = os.path.join(output_dir, 'database.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        raise Exception(f"Failed to export dashboards: {response.text}")
    
def import_dashboard(access_token,csrf_token,zip_file_path,session,url):
    url = f"{url}/api/v1/dashboard/import"
    with open(zip_file_path, 'rb') as file:
        files = {'formData': ('dashboard.zip', file, 'application/zip')}
        payload={'passwords': '{"databases/{{DatabaseYAMLFile}}": "{{DatabasePassword}}"}','overwrite': 'true'}
        headers = {"Authorization": f"Bearer {access_token}", 'Accept': 'application/json','X-CSRFToken': csrf_token,"Referer":f"{url}/api/v1/security/csrf_token/"}
        response = session.post(url,files=files,headers=headers,data=payload)

        if response.status_code != 200:
            raise Exception(f"Failed to import dashboard: {response.text}")
        return response.text
def importdashboard():
    if (getdomain1.get()==""):
        messagebox.showinfo('Error!', 'Input first domain!')
    else:
        domain1=getdomain1.get()
    if (getdomain2.get()==""):
        messagebox.showinfo('Error!', 'Input second domain!')
    else:
        domain2=getdomain2.get()
    if (getusername1.get()==""):
        messagebox.showinfo('Error!', 'Input first username!')
    else:
        username1=getusername1.get()
    if (getpassword1.get()==""):
        messagebox.showinfo('Error!', 'Input first passowrd!')
    else:
        password1=getpassword1.get()
    if (getusername2.get()==""):
        messagebox.showinfo('Error!', 'Input second username!')
    else:
        username2=getusername2.get()
    if (getpassword2.get()==""):
        messagebox.showinfo('Error!', 'Input second password!')
    else:
        password2=getpassword2.get()
    if (getdashboardname.get()==""):
        messagebox.showinfo('Error!', "Input dashboad's name!")
    else:
        dashboardname=getdashboardname.get()
    print(domain1,domain2,username1,username2,password1,password2,dashboardname)
    exportsession=requests.Session()
    refresh_token1,access_token1=get_access_token(exportsession,domain1,password1,username1)
    dashboardid1=get_dashboards_id(access_token1,dashboardname,domain1,exportsession)
    export_dashboards(access_token1, dashboardid1, "./",domain1,exportsession,"dashboard1")

    importsession=requests.Session()
    refresh_token2,access_token2=get_access_token(importsession,domain2,password2,username2)
    dashboardid2=get_dashboards_id(access_token2,dashboardname,domain2,importsession)
    if (len(dashboardid1)>0):      
        if (len(dashboardid2)>0):    
            export_dashboards(access_token2, dashboardid2, "./",domain2,importsession,"dashboard2")
            updatedashboard("./dashboard1.zip","./dashboard2.zip")
            csrf_token2=get_csrf_token(importsession,domain2,access_token2)
            import_dashboard(access_token2,csrf_token2,"./dashboard1.zip",importsession,domain2)
            os.remove("./dashboard1.zip")
            os.remove("./dashboard2.zip")
        else:
            databaseids=get_database_id(access_token2,domain2,importsession)
            export_database(access_token2, [databaseids[-1]], ".",domain2,importsession)
            with zipfile.ZipFile("./database.zip", 'r') as zip_ref:
                zip_ref.extractall(path="./database")
            secondpath="./database/"+os.listdir("./database")[0]+"/databases/"+os.listdir("./database/"+os.listdir("./database")[0]+"/databases")[0]
            changedb("./dashboard1.zip",secondpath)
            shutil.rmtree("./database")
            os.remove("./database.zip")
            csrf_token2=get_csrf_token(importsession,domain2,access_token2)
            import_dashboard(access_token2,csrf_token2,"./dashboard1.zip",importsession,domain2)
            os.remove("./dashboard1.zip")
    else:
        messagebox.showinfo('Error!', "No such dashboard on first superset server")


window = Tk()  
window.title("Superset Import App")  
window.geometry('400x350')


getdomain1label=Label(window,text="Domain of first superset server:")
getdomain1label.grid(column=1, row=1)
getdomain1=Entry(window,width=30)
getdomain1.grid(column=1, row=2)
getdomain2label=Label(window,text="Domain of second superset server:")
getdomain2label.grid(column=1, row=3)
getdomain2=Entry(window,width=30)
getdomain2.grid(column=1, row=4)
getusername1label=Label(window,text="Your username on server where you will import dashboard into")
getusername1label.grid(column=1, row=5)
getusername1=Entry(window,width=30)
getusername1.grid(column=1, row=6)
getpassword1label=Label(window,text="Your password on server where you will import dashboard into")
getpassword1label.grid(column=1, row=7)
getpassword1=Entry(window,width=30)
getpassword1.grid(column=1, row=8)
getusername2label=Label(window,text="Your username on server where you will import dashboard from")
getusername2label.grid(column=1, row=9)
getusername2=Entry(window,width=30)
getusername2.grid(column=1, row=10)
getpassword2label=Label(window,text="Your password on server where you will import dashboard from")
getpassword2label.grid(column=1, row=11)
getpassword2=Entry(window,width=30)
getpassword2.grid(column=1, row=12)
getdashboardnamelabel=Label(window,text="Name of dashboard")
getdashboardnamelabel.grid(column=1, row=13)
getdashboardname=Entry(window,width=30)
getdashboardname.grid(column=1, row=14)
importall=Button(window, text="Import", command=importdashboard)  
importall.grid(column=1, row=15)
window.mainloop()


exportsession=requests.Session()
refresh_token1,access_token1=get_access_token(exportsession,domain1,password1,username1)
dashboardid1=get_dashboards_id(access_token1,dashboardname,domain1,exportsession)
export_dashboards(access_token1, dashboardid1, "./",domain1,exportsession,"dashboard1")

importsession=requests.Session()
refresh_token2,access_token2=get_access_token(importsession,domain2,password2,username2)
dashboardid2=get_dashboards_id(access_token2,dashboardname,domain2,importsession)
if (len(dashdoardid1)>0):      
    if (len(dashboardid2)>0):    
        export_dashboards(access_token2, dashboardid2, "./",domain2,importsession,"dashboard2")
        updatedashboard("./dashboard1.zip","./dashboard2.zip")
        csrf_token2=get_csrf_token(importsession,domain2,access_token2)
        import_dashboard(access_token2,csrf_token2,"./dashboard1.zip",importsession,domain2)
        os.remove("./dashboard1.zip")
        os.remove("./dashboard2.zip")
    else:
        databaseids=get_database_id(access_token2,domain2,importsession)
        export_database(access_token2, [databaseids[-1]], ".",domain2,importsession)
        with zipfile.ZipFile("./database.zip", 'r') as zip_ref:
            zip_ref.extractall(path="./database")
        secondpath="./database/"+os.listdir("./database")[0]+"/databases/"+os.listdir("./database/"+os.listdir("./database")[0]+"/databases")[0]
        print(secondpath)
        changedb("./dashboard1.zip",secondpath)
        shutil.rmtree("./database")
        os.remove("./database.zip")
        csrf_token2=get_csrf_token(importsession,domain2,access_token2)
        import_dashboard(access_token2,csrf_token2,"./dashboard1.zip",importsession,domain2)
        os.remove("./dashboard1.zip")
else:
    print("No such dashboard on first superset server")
