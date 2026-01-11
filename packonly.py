#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import struct
import sys

def pack_packonly(input_dir, output_file):
    # 收集所有文件
    files = []
    for root, dirs, filenames in os.walk(input_dir):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            files.append(full_path)
    
    if not files:
        print(f"错误：在目录 {input_dir} 中未找到任何文件")
        return False
    
    print(f"找到 {len(files)} 个文件")
    
    with open(output_file, 'wb') as fout:
        # 写入文件头
        header = struct.pack('<8s56sII', 
                           b'PackOnly',        # magic
                           b'\x00' * 56,       # reserved
                           len(files),         # index_entries
                           0)                  # pad
        fout.write(header)
        
        # 计算偏移并写入索引
        current_offset = len(header) + 144 * len(files)  # 144 = sizeof(pdpack_entry_t)
        
        for filepath in files:
            # 获取相对路径
            rel_path = os.path.relpath(filepath, input_dir)
            # 转换为ASCII，限制128字节
            name_bytes = rel_path.encode('shift_jis', errors='replace')[:127] + b'\x00'
            
            # 获取文件大小
            file_size = os.path.getsize(filepath)
            
            # 写入索引条目
            entry = struct.pack('<128sIIII',
                              name_bytes.ljust(128, b'\x00'),
                              current_offset,  # offset
                              0,              # pad0
                              file_size,      # length
                              0)              # pad1
            fout.write(entry)
            
            current_offset += file_size
        
        # 写入文件数据
        for filepath in files:
            print(f"打包: {os.path.relpath(filepath, input_dir)}")
            with open(filepath, 'rb') as fin:
                data = fin.read()
                
                # 如果不是PNG文件，处理第0x1A字节
                if not filepath.lower().endswith('.png') and len(data) > 0x1A:
                    data = bytearray(data)
                    data[0x1A] ^= 0xFF
                    data = bytes(data)
                
                fout.write(data)
    
    print(f"\n成功打包到: {output_file}")
    print(f"总计文件大小: {os.path.getsize(output_file)} 字节")
    return True

def main():
    if len(sys.argv) != 3:
        print("PackOnly打包工具")
        print("使用方法: python packonly.py <输入目录> <输出文件.pd>")
        print("示例: python packonly.py cg_data cg.pd")
        return
    
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_dir):
        print(f"错误：目录不存在: {input_dir}")
        return
    
    pack_packonly(input_dir, output_file)

if __name__ == '__main__':
    main()