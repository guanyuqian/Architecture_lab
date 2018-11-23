proj1
===========================

### 项目简介
```
Implement a MIPS simulator that can perform the following steps:
	1. load a specified MIPS text file.
	2. generate the assembly code.
	3. perform instruction-by-instruction simulation of the generated assembly.
```
* GIT地址    ：https://github.com/guanyuqian/Architecture_lab.git
* 项目目录   ：[guanyuqian/**Architecture_lab**/proj1](https://github.com/guanyuqian/Architecture_lab/tree/master/proj1)

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

 [文档路径：/proj1/doc](https://github.com/guanyuqian/Architecture_lab/tree/master/proj1/doc) 

1. [Fall2018.pdf](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/Fall2018.pdf) 
1. [code_analysis.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/code_analysis.txt) 
1. [disassembly - 副本.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/disassembly%20-%20%E5%89%AF%E6%9C%AC.txt) 
1. [disassembly.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/disassembly.txt) 
1. [mips.pdf](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/mips.pdf) 
1. [projct details.docx](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/projct%20details.docx) 
1. [sample - 副本.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/sample%20-%20%E5%89%AF%E6%9C%AC.txt) 
1. [sample.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/sample.txt) 
1. [simulation.txt](https://github.com/guanyuqian/Architecture_lab/blob/master/proj1/doc/simulation.txt) 
