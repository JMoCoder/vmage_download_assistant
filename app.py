#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号图片下载助手 - 主应用文件

这是一个Flask应用，提供API接口用于解析微信公众号文章并下载其中的图片。
主要功能包括：
1. 解析微信公众号文章链接
2. 提取文章中的图片链接
3. 智能筛选图片（排除头像、装饰图等）
4. 批量下载图片并打包
"""

import os
import re
import json
import time
import zipfile
import hashlib
import tempfile
import threading
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import requests
from bs4 import BeautifulSoup
from PIL import Image
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import concurrent.futures

# 应用配置
app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

# 全局配置
if os.environ.get('VERCEL'):
    # Vercel环境使用/tmp目录
    DOWNLOAD_FOLDER = "/tmp/downloads"
    TEMP_FOLDER = "/tmp/temp"
else:
    # 本地环境使用当前目录
    DOWNLOAD_FOLDER = "downloads"  # 下载文件夹
    TEMP_FOLDER = "temp"          # 临时文件夹
MAX_WORKERS = 5               # 最大并发下载数
REQUEST_TIMEOUT = 30          # 请求超时时间
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 最大图片大小 50MB

# 创建必要的文件夹
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# 请求头配置，模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 全局变量用于存储处理状态
processing_status = {}

class WeChatImageExtractor:
    """微信公众号图片提取器类"""
    
    def __init__(self):
        """初始化提取器"""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def validate_url(self, url: str) -> bool:
        """
        验证是否为有效的微信公众号文章链接
        
        Args:
            url: 待验证的URL
            
        Returns:
            bool: 是否为有效链接
        """
        # 微信公众号文章链接的正则表达式
        wechat_patterns = [
            r'https?://mp\.weixin\.qq\.com/s/',
            r'https?://mp\.weixin\.qq\.com/s\?',
        ]
        
        return any(re.match(pattern, url) for pattern in wechat_patterns)
    
    def fetch_article_content(self, url: str) -> Tuple[bool, str, str]:
        """
        获取文章内容
        
        Args:
            url: 文章链接
            
        Returns:
            Tuple[bool, str, str]: (是否成功, HTML内容, 错误信息)
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return True, response.text, ""
        except requests.exceptions.RequestException as e:
            return False, "", f"获取文章内容失败: {str(e)}"
    
    def extract_images_from_html(self, html_content: str, base_url: str) -> List[Dict]:
        """
        从HTML内容中提取图片信息
        
        Args:
            html_content: HTML内容
            base_url: 基础URL用于相对链接转换
            
        Returns:
            List[Dict]: 图片信息列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []
        
        # 查找所有img标签
        img_tags = soup.find_all('img')
        
        for i, img in enumerate(img_tags):
            img_info = self._extract_single_image_info(img, base_url, i)
            if img_info:
                images.append(img_info)
        
        return images
    
    def _extract_single_image_info(self, img_tag, base_url: str, index: int) -> Optional[Dict]:
        """
        提取单个图片的信息
        
        Args:
            img_tag: img标签对象
            base_url: 基础URL
            index: 图片索引
            
        Returns:
            Optional[Dict]: 图片信息字典或None
        """
        # 获取图片URL，优先级：data-src > src
        img_url = img_tag.get('data-src') or img_tag.get('src')
        if not img_url:
            return None
        
        # 转换为绝对URL
        img_url = urljoin(base_url, img_url)
        
        # 尝试获取高清版本的URL
        hd_url = self._get_hd_image_url(img_url)
        
        # 获取图片属性
        alt_text = img_tag.get('alt', '')
        width = img_tag.get('width', '')
        height = img_tag.get('height', '')
        
        return {
            'index': index,
            'original_url': img_url,
            'hd_url': hd_url,
            'alt': alt_text,
            'width': width,
            'height': height,
            'size': 0,  # 将在下载时获取
            'format': '',  # 将在下载时获取
        }
    
    def _get_hd_image_url(self, img_url: str) -> str:
        """
        获取高清版本的图片URL
        
        Args:
            img_url: 原始图片URL
            
        Returns:
            str: 高清图片URL
        """
        # 微信图片URL规律处理
        if 'mmbiz.qpic.cn' in img_url:
            # 移除尺寸限制参数，获取原图
            if 'wx_fmt=' in img_url:
                # 保留格式参数，移除其他尺寸参数
                base_url = img_url.split('?')[0]
                format_match = re.search(r'wx_fmt=(\w+)', img_url)
                if format_match:
                    return f"{base_url}?wx_fmt={format_match.group(1)}"
            return img_url
        
        return img_url
    
    def filter_images(self, images: List[Dict], options: Dict) -> List[Dict]:
        """
        根据选项筛选图片
        
        Args:
            images: 图片列表
            options: 筛选选项
            
        Returns:
            List[Dict]: 筛选后的图片列表
        """
        filtered_images = []
        skipped_count = 0
        
        for img in images:
            # 跳过明显的头像和装饰图
            if self._should_skip_image(img, options):
                skipped_count += 1
                continue
                
            filtered_images.append(img)
        

        return filtered_images
    
    def _should_skip_image(self, img_info: Dict, options: Dict) -> bool:
        """
        判断是否应该跳过该图片
        
        Args:
            img_info: 图片信息
            options: 筛选选项
            
        Returns:
            bool: 是否跳过
        """
        # 检查是否排除头像图片
        if options.get('excludeAvatar', False):
            alt_text = img_info.get('alt', '').lower()
            skip_keywords = ['avatar', 'logo', 'qrcode', '二维码', '头像', '扫码']
            
            if any(keyword in alt_text for keyword in skip_keywords):
                return True
            
            # 根据URL特征筛选
            url = img_info.get('original_url', '')
            if 'avatar' in url or 'logo' in url:
                return True
        
        # 检查是否排除GIF动图
        if options.get('excludeGif', False):
            url = img_info.get('original_url', '')
            # 检查URL中是否包含gif格式
            if 'gif' in url.lower() or url.lower().endswith('.gif'):

                return True
            # 检查URL参数中的格式
            if 'wx_fmt=gif' in url.lower():

                return True
        
        # 检查是否排除小尺寸图片
        if options.get('excludeSmall', False):
            try:
                # 安全地转换为整数
                width = int(img_info.get('width', 0)) if img_info.get('width') else 0
                height = int(img_info.get('height', 0)) if img_info.get('height') else 0
                # 如果有尺寸信息且都小于100像素，则认为是小图片
                if width > 0 and height > 0 and width < 100 and height < 100:

                    return True
            except (ValueError, TypeError):
                # 如果转换失败，忽略尺寸检查
                pass
            # 根据URL特征判断小图片
            url = img_info.get('original_url', '')
            if '/64' in url or '/32' in url or 'thumb' in url.lower():

                return True
        
        return False
    
    def download_images(self, images: List[Dict], task_id: str, options: Dict) -> Tuple[List[str], List[str]]:
        """
        批量下载图片
        
        Args:
            images: 图片列表
            task_id: 任务ID
            options: 下载选项
            
        Returns:
            Tuple[List[str], List[str]]: (成功下载的文件路径列表, 错误信息列表)
        """
        successful_downloads = []
        errors = []
        
        # 创建任务专用临时文件夹
        task_folder = os.path.join(TEMP_FOLDER, task_id)
        os.makedirs(task_folder, exist_ok=True)
        
        # 使用线程池并发下载
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_img = {
                executor.submit(self._download_single_image, img, task_folder, i, options): (img, i)
                for i, img in enumerate(images)
            }
            
            for future in concurrent.futures.as_completed(future_to_img):
                img_info, img_index = future_to_img[future]
                try:
                    result = future.result()
                    if result['success']:
                        successful_downloads.append(result['file_path'])
                        # 更新处理状态
                        self._update_progress(task_id, img_index + 1, len(images), 
                                           f"已下载: {result['filename']}")
                    else:
                        errors.append(f"图片 {img_index + 1}: {result['error']}")
                except Exception as e:
                    errors.append(f"图片 {img_index + 1}: {str(e)}")
        
        return successful_downloads, errors
    
    def _download_single_image(self, img_info: Dict, task_folder: str, index: int, options: Dict = None) -> Dict:
        """
        下载单个图片
        
        Args:
            img_info: 图片信息
            task_folder: 任务文件夹路径
            index: 图片索引
            options: 下载选项
            
        Returns:
            Dict: 下载结果
        """
        try:
            # 根据选项决定使用高清版本还是普通版本
            if options and options.get('getOriginal', True):
                # 优先使用高清版本
                img_url = img_info.get('hd_url') or img_info.get('original_url')
            else:
                # 使用普通版本
                img_url = img_info.get('original_url')
            
            # 发送下载请求
            response = self.session.get(img_url, timeout=REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                return {'success': False, 'error': '图片文件过大'}
            
            # 获取文件扩展名
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type:
                ext = '.jpg'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/webp' in content_type:
                ext = '.webp'
            elif 'image/gif' in content_type:
                ext = '.gif'
            else:
                # 从URL中推断扩展名
                parsed_url = urlparse(img_url)
                path_ext = os.path.splitext(parsed_url.path)[1]
                ext = path_ext if path_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif'] else '.jpg'
            
            # 生成文件名
            filename = f"image_{index + 1:03d}{ext}"
            file_path = os.path.join(task_folder, filename)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证图片文件
            try:
                with Image.open(file_path) as pil_img:
                    img_info['width'] = pil_img.width
                    img_info['height'] = pil_img.height
                    img_info['format'] = pil_img.format
                    img_info['size'] = os.path.getsize(file_path)
            except Exception:
                # 如果不是有效图片，仍然保留文件
                img_info['size'] = os.path.getsize(file_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'size': img_info['size']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_progress(self, task_id: str, current: int, total: int, message: str):
        """
        更新处理进度
        
        Args:
            task_id: 任务ID
            current: 当前进度
            total: 总数
            message: 状态消息
        """
        if task_id in processing_status:
            processing_status[task_id].update({
                'current': current,
                'total': total,
                'progress': (current / total) * 100 if total > 0 else 0,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
    
    def create_zip_file(self, file_paths: List[str], task_id: str) -> str:
        """
        创建ZIP压缩文件
        
        Args:
            file_paths: 要压缩的文件路径列表
            task_id: 任务ID
            
        Returns:
            str: ZIP文件路径
        """
        zip_filename = f"wechat_images_{task_id}.zip"
        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    zipf.write(file_path, filename)
        
        return zip_path


# Flask 路由定义

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_article():
    """
    分析微信公众号文章API接口
    
    请求参数：
    - url: 文章链接
    - options: 分析选项
    
    返回：
    - success: 是否成功
    - task_id: 任务ID
    - images: 图片列表（如果成功）
    - error: 错误信息（如果失败）
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        options = data.get('options', {})
        
        if not url:
            return jsonify({'success': False, 'error': '请提供有效的文章链接'})
        
        # 创建提取器实例
        extractor = WeChatImageExtractor()
        
        # 验证URL
        if not extractor.validate_url(url):
            return jsonify({'success': False, 'error': '不是有效的微信公众号文章链接'})
        
        # 生成任务ID
        task_id = hashlib.md5(f"{url}{int(time.time())}".encode()).hexdigest()[:16]
        
        # 初始化处理状态
        processing_status[task_id] = {
            'status': 'analyzing',
            'progress': 0,
            'current': 0,
            'total': 0,
            'message': '正在分析文章...',
            'timestamp': datetime.now().isoformat()
        }
        
        # 获取文章内容
        success, html_content, error = extractor.fetch_article_content(url)
        if not success:
            processing_status[task_id]['status'] = 'error'
            processing_status[task_id]['message'] = error
            return jsonify({'success': False, 'error': error})
        
        # 提取图片
        processing_status[task_id]['message'] = '正在提取图片...'
        images = extractor.extract_images_from_html(html_content, url)
        
        if not images:
            processing_status[task_id]['status'] = 'error'
            processing_status[task_id]['message'] = '文章中未找到图片'
            return jsonify({'success': False, 'error': '文章中未找到图片'})
        
        # 筛选图片
        processing_status[task_id]['message'] = '正在筛选图片...'
        filtered_images = extractor.filter_images(images, options)
        
        # 更新状态
        processing_status[task_id].update({
            'status': 'ready',
            'message': f'分析完成，找到 {len(filtered_images)} 张图片',
            'total': len(filtered_images),
            'images': filtered_images
        })
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'images': filtered_images,
            'total_count': len(filtered_images)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'分析失败: {str(e)}'})


@app.route('/api/download', methods=['POST'])
def download_images():
    """
    下载图片API接口
    
    请求参数：
    - task_id: 任务ID
    - selected_indices: 选中的图片索引列表（可选，默认全部）
    - options: 下载选项
    
    返回：
    - success: 是否成功
    - download_url: 下载链接（如果成功）
    - error: 错误信息（如果失败）
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        selected_indices = data.get('selected_indices', [])
        options = data.get('options', {})
        
        if not task_id or task_id not in processing_status:
            return jsonify({'success': False, 'error': '无效的任务ID'})
        
        task_info = processing_status[task_id]
        if task_info['status'] != 'ready':
            return jsonify({'success': False, 'error': '任务未准备就绪'})
        
        images = task_info.get('images', [])
        if not images:
            return jsonify({'success': False, 'error': '没有可下载的图片'})
        
        # 筛选要下载的图片
        if selected_indices:
            images_to_download = [img for i, img in enumerate(images) if i in selected_indices]
        else:
            images_to_download = images
        
        if not images_to_download:
            return jsonify({'success': False, 'error': '没有选中要下载的图片'})
        
        # 更新状态为下载中
        processing_status[task_id].update({
            'status': 'downloading',
            'message': '开始下载图片...',
            'progress': 0,
            'current': 0,
            'total': len(images_to_download)
        })
        
        # 启动后台下载任务
        def download_task():
            extractor = WeChatImageExtractor()
            
            try:
                # 下载图片
                successful_downloads, errors = extractor.download_images(
                    images_to_download, task_id, options
                )
                
                if successful_downloads:
                    # 创建ZIP文件
                    processing_status[task_id]['message'] = '正在打包文件...'
                    zip_path = extractor.create_zip_file(successful_downloads, task_id)
                    
                    # 更新状态为完成
                    processing_status[task_id].update({
                        'status': 'completed',
                        'message': f'下载完成，成功下载 {len(successful_downloads)} 张图片',
                        'zip_path': zip_path,
                        'successful_count': len(successful_downloads),
                        'error_count': len(errors),
                        'errors': errors
                    })
                else:
                    processing_status[task_id].update({
                        'status': 'error',
                        'message': '下载失败，没有成功下载任何图片',
                        'errors': errors
                    })
                    
            except Exception as e:
                processing_status[task_id].update({
                    'status': 'error',
                    'message': f'下载失败: {str(e)}'
                })
        
        # 在后台线程中执行下载
        threading.Thread(target=download_task, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': '下载任务已启动',
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'启动下载失败: {str(e)}'})


@app.route('/api/status/<task_id>')
def get_task_status(task_id):
    """
    获取任务状态API接口
    
    参数：
    - task_id: 任务ID
    
    返回：
    - 任务状态信息
    """
    if task_id not in processing_status:
        return jsonify({'success': False, 'error': '任务不存在'})
    
    return jsonify({
        'success': True,
        'status': processing_status[task_id]
    })


@app.route('/api/download-file/<task_id>')
def download_file(task_id):
    """
    下载文件API接口
    
    参数：
    - task_id: 任务ID
    
    返回：
    - ZIP文件
    """
    if task_id not in processing_status:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task_info = processing_status[task_id]
    if task_info['status'] != 'completed':
        return jsonify({'success': False, 'error': '任务未完成'}), 400
    
    zip_path = task_info.get('zip_path')
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({'success': False, 'error': '文件不存在'}), 404
    
    return send_file(
        zip_path,
        as_attachment=True,
        download_name=f"微信公众号图片_{task_id}.zip",
        mimetype='application/zip'
    )


@app.route('/api/proxy-image')
def proxy_image():
    """
    图片代理接口，用于解决微信图片防盗链问题
    
    参数：
    - url: 图片URL
    
    返回：
    - 图片数据
    """
    try:
        img_url = request.args.get('url')
        if not img_url:
            print(f"[代理错误] 缺少图片URL参数")
            return jsonify({'success': False, 'error': '缺少图片URL参数'}), 400
        
        print(f"[代理请求] 尝试代理图片: {img_url[:100]}...")
        
        # 创建session用于请求图片
        session = requests.Session()
        
        # 设置更完整的请求头来模拟微信客户端
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://mp.weixin.qq.com/',
        })
        
        # 请求图片
        response = session.get(img_url, timeout=15, stream=True)
        print(f"[代理响应] 状态码: {response.status_code}, Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"[代理重试] 第一次请求失败，状态码: {response.status_code}，尝试移动端User-Agent")
            # 如果第一次失败，尝试不同的User-Agent
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1 wechatdevtools/1.05.2109300 MicroMessenger/8.0.5 Language/zh_CN webview/',
            })
            response = session.get(img_url, timeout=15, stream=True)
            print(f"[代理重试] 重试结果状态码: {response.status_code}")
        
        response.raise_for_status()
        
        # 获取图片的content-type
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # 检查是否是图片
        if not content_type.startswith('image/'):
            return jsonify({'success': False, 'error': '不是有效的图片'}), 400
        
        # 检查图片大小
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB限制
            return jsonify({'success': False, 'error': '图片文件过大'}), 400
        
        # 读取图片数据
        image_data = b''
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                image_data += chunk
                # 防止内存溢出
                if len(image_data) > 10 * 1024 * 1024:  # 10MB限制
                    return jsonify({'success': False, 'error': '图片文件过大'}), 400
        
        # 验证图片数据
        if len(image_data) < 100:  # 图片太小，可能是错误页面
            print(f"[代理错误] 图片数据太小: {len(image_data)} 字节")
            return jsonify({'success': False, 'error': '图片数据无效'}), 400
        
        print(f"[代理成功] 图片大小: {len(image_data)} 字节, Content-Type: {content_type}")
        
        # 返回图片数据
        from flask import Response
        return Response(
            image_data,
            mimetype=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',  # 缓存1小时
                'Access-Control-Allow-Origin': '*',  # 允许跨域
                'Content-Length': str(len(image_data)),
            }
        )
        
    except requests.exceptions.Timeout:
        print(f"[代理错误] 图片加载超时: {img_url[:100]}...")
        return jsonify({'success': False, 'error': '图片加载超时'}), 504
    except requests.exceptions.RequestException as e:
        print(f"[代理错误] 请求异常: {str(e)}")
        return jsonify({'success': False, 'error': f'图片加载失败: {str(e)}'}), 502
    except Exception as e:
        print(f"[代理错误] 未知异常: {str(e)}")
        return jsonify({'success': False, 'error': f'代理失败: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'success': False, 'error': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 开发模式运行
    print("微信公众号图片下载助手启动中...")
    print(f"下载文件夹: {os.path.abspath(DOWNLOAD_FOLDER)}")
    print(f"临时文件夹: {os.path.abspath(TEMP_FOLDER)}")
    
    app.run(
        debug=True,  # 开发模式
        host='0.0.0.0',  # 允许外部访问
        port=5000,  # 端口号
        threaded=True  # 启用多线程
    )