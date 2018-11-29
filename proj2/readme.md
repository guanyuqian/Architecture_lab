proj1
===========================

### 项目简介
```
Implement a MIPS simulator that can perform the following steps:
•	load a specified MIPS text file.
•	perform pipelined simulation and print the register/buffer/memory contents.
```
* GIT地址    ：https://github.com/guanyuqian/Architecture_lab.git
* 项目目录   ：[guanyuqian/**Architecture_lab**/proj2](https://github.com/guanyuqian/Architecture_lab/tree/master/proj2)

### 环境依赖
```
Python3.5以上
```

### 注意事项

- 程序的输入和输出都是有default值，可以省略参数直接运行，默认输入和输出在项目相对路径下
- 本程序在windows平台开发，如果在linux等别的平台下面运行，或许要注意一下指定文件时路径的规范问题

### 运行程序

```shell
py main.py input_file_str output1_file_str output2_file_str
```

- py——python
- main.py——MIPS仿真程序入口
- input_file_str——机器代码输入文件（default :  **sample_int.txt** ）
- output1_file_str——解析机器代码生成汇编输出文件（default :  **disassembly_int.txt** ）
- output2_file_str——仿真执行输出文件（default :  **simulation_int.txt** ）

### 开发文档

 [文档路径：/proj2/doc](https://github.com/guanyuqian/Architecture_lab/tree/master/proj2/doc) 

### PS
- 本项目实现并行处理IF，ISSUE，EXE，WB四个过程
- doc未要求store命令要在load后执行，但这是必要的，不然会有内存读写错误