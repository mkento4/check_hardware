# coding: utf-8
import psutil
import datetime
import matplotlib.pyplot as plt
from multiprocessing import *
import numpy as np
import subprocess
import time
import re
import json
import os
import csv
"""
cpu,gpu,memory の使用率を調査する

学習を回している間、同時にcheck.pyも起動しておく

checkはずっと繰り返して行うため、multiprocessingを使用して関数を並列化している

Usage:
from check import check_gpu
①from multiprocessing import *
②スレッドのインスタンス化

#おまじない
command = Value('i',0)
command.value = 0

check_gpu_thread = Process(name='check_gpu', target=check_gpu,command)
③インスタンス化したものをスタートさせる
check_gpu_thread.start()

今printはコメントアウトしてありますのでログをみたい場合は該当する関数についてprintをコメントアウトから解除してください。

サンプルコードは同じディレクトリのtest_check.pyに書いております

"""
 #ファイル名に自動で日付が入るようにする
titletime = datetime.datetime.now().strftime('%m%d%H%M')

#履歴を保存するディレクトリ

#一時的に情報を保存する
cpu_use_history = []
gpu_use_history = []
gpu_mem_history = []
cpu_mem_history = []

def check_cpu(command, save_path='./cpu_use_history/'):
    
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    save_name = save_path + titletime + '.png'

    try:

        while command.value == 0:

            #それぞれのコアあたりのcpu使用率を取得
            info = psutil.cpu_percent(interval=3, percpu=True)
            clock = psutil.cpu_freq()

            #取得したものをappendする
            cpu_use_history.append(info)

            #debug ログをみたい場合はコメントアウトを外してください
            # print(info)
            # print('clock',clock)
        
        

    except Exception as e:
        print('debug',e)

    
    #調査した回数分　横軸
    x = np.linspace(0, len(cpu_use_history), len(cpu_use_history))
    y = cpu_use_history

    #プロット
    plt.plot(x,y,label='cpu使用率',linewidth=0.5)

    with open(save_path+str(titletime)+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(cpu_use_history)

    #save
    plt.savefig(save_name)

def check_gpu(command,save_path='./gpu_use_history/'):
    save_name = save_path + titletime + '.png'

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    try:
        while command.value == 0:

            #コマンドをpython上で動かす
            info = subprocess.check_output(["/opt/rocm/bin/rocm-smi", "-u","--json"])

            #binaryファイルなのでデコードして、jsonで読み込む
            info = info.decode('utf8')
            info = json.loads(info)

            #card1 card0 とログに表記されていた
            card1 = float(info["card1"]['GPU use (%)']) #GPU[0]
            card0 = float(info["card0"]['GPU use (%)']) #GPU[1]

            #取得したものをappend
            gpu_use_history.append([card1,card0])

            #debug
            # print(f"card1 :{card1} , card0 :{card0}")

            #0.5秒停止
            time.sleep(0.5)
    except Exception as e:
        print('debug',e)

    x = np.linspace(0, len(gpu_use_history), len(gpu_use_history))
    y = gpu_use_history 

    #プロット
    plt.plot(x,y,label='gpuの使用率',linewidth=0.5)

    with open(save_path+str(titletime)+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(gpu_use_history)
    

    plt.savefig(save_name)


#cpuのメモリを確認する
def check_cpu_mem(command,save_path='./cpu_mem_history/'):
    #ファイル名に自動で日付が入るようにする
    save_name = save_path + titletime + '.png'

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    try:

        while command.value == 0:

            #それぞれのコアあたりのcpu使用率を取得
            info = psutil.virtual_memory()

            #取得したものをappendする
            cpu_mem_history.append(info.percent)

            #debug
            # print(info)
            time.sleep(0.5)
    except Exception as e:
        print('debug',e)    
    
    #調査した回数分　横軸
    x = np.linspace(0, len(cpu_mem_history), len(cpu_mem_history))
    y = cpu_mem_history 

    #プロット
    plt.plot(x,y,label='mem使用率',linewidth=0.5)

    #save
    plt.savefig(save_name)

    with open(save_path+str(titletime)+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(cpu_mem_history)

def check_gpu_mem(command,save_path='./gpu_mem_history/'):
    save_name = save_path + titletime + '.png'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    try:
        while command.value == 0:

            #コマンドをpython上で動かす
            info = subprocess.check_output(["/opt/rocm/bin/rocm-smi", "--showmemuse","--json"])

            #binaryファイルなのでデコードして、jsonで読み込む
            info = info.decode('utf8')
            info = json.loads(info)

            #card1 card0 とログに表記されていた
            card1 = float(info["card1"]['GPU memory use (%)']) #GPU[0]
            card0 = float(info["card0"]['GPU memory use (%)']) #GPU[1]

            #取得したものをappend
            gpu_mem_history.append([card1,card0])

            #debug
            # print(f"card1 mem :{card1} , card0 mem :{card0}")

            #0.5秒停止
            time.sleep(0.5)
        
    except Exception as e:
        print('debug',e)

    x = np.linspace(0, len(gpu_mem_history), len(gpu_mem_history))
    y = gpu_mem_history 

    #プロット
    plt.plot(x,y,label='gpuの使用率',linewidth=0.5)
    
    with open(save_path+str(titletime)+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(gpu_mem_history)

    plt.savefig(save_name)
    

if __name__ == "__main__":

    #command生成(終了スイッチみたいなもの)
    command = Value('i',0)
    command.value = 0

    check_cpu_thread = Process(name='check_cpu', target=check_cpu,args=(command,))
    check_gpu_thread = Process(name='check_gpu', target=check_gpu,args=(command,))
    check_cpu_mem_thread = Process(name='check_cpu_mem', target=check_cpu_mem,args=(command,))
    check_gpu_mem_thread = Process(name='check_gpu_mem', target=check_gpu_mem,args=(command,))
    
    check_cpu_thread.start()
    check_gpu_thread.start()
    check_cpu_mem_thread.start()
    check_gpu_mem_thread.start()

    while True:
        end = input('終了させるには end を入力していください\n')
        if end == 'end':
            command.value = 1
            break