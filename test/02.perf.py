# file: 100_rounds_perf_test.py
import asyncio
import aiohttp
import time
import os
from pathlib import Path
import pyrootutils

ROOT = pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

async def send_tts_request(session, base_url, text, speaker, output_dir, request_id, round_id):
    """
    发送单个TTS请求（协程版本）
    
    Args:
        session: aiohttp客户端会话
        base_url: 服务基础URL
        text: 要转换的文本
        speaker: 角色名
        output_dir: 输出目录
        request_id: 请求ID，用于标识
        round_id: 轮次ID
    
    Returns:
        dict: 包含请求结果信息的字典
    """
    print(f"Round {round_id}, Request {request_id}: {text[:30]}{'...' if len(text) > 30 else ''}")
    
    # 准备请求数据
    payload = {
        "text": text,
        "character": speaker
    }
    
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 发送TTS请求
        async with session.post(f"{base_url}/tts", json=payload) as response:
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            if response.status == 200:
                # 读取响应内容（在大批量测试中可以选择不保存文件以提高性能）
                content = await response.read()
                
                # 生成文件名
                safe_text = "".join(c for c in text[:10] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"round{round_id}_{speaker}_{request_id}_{safe_text}_{elapsed_time:.2f}s.wav"
                filepath = os.path.join(output_dir, filename)
                
                # 保存音频文件
                with open(filepath, "wb") as f:
                    f.write(content)
                
                print(f"  Round {round_id}, Request {request_id} saved: {filename} (took {elapsed_time:.2f}s)")
                return {
                    "round_id": round_id,
                    "request_id": request_id,
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "filename": filename
                }
            else:
                text_content = await response.text()
                print(f"  Round {round_id}, Request {request_id} error: {response.status} - {text_content}")
                return {
                    "round_id": round_id,
                    "request_id": request_id,
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "error": f"HTTP {response.status}: {text_content}"
                }
                
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"  Round {round_id}, Request {request_id} exception occurred: {str(e)}")
        return {
            "round_id": round_id,
            "request_id": request_id,
            "success": False,
            "elapsed_time": elapsed_time,
            "error": str(e)
        }

async def run_test_round(session, base_url, texts, speaker, output_dir, round_id, concurrency_level):
    """
    运行一轮并发测试
    
    Args:
        session: aiohttp客户端会话
        base_url: 服务基础URL
        texts: 文本列表
        speaker: 角色名
        output_dir: 输出目录
        round_id: 轮次ID
        concurrency_level: 并发数
    
    Returns:
        list: 本轮所有请求的结果列表
    """
    # 创建本轮的所有任务
    tasks = [
        send_tts_request(
            session, 
            base_url, 
            texts[i % len(texts)], 
            speaker, 
            output_dir, 
            i+1,
            round_id
        )
        for i in range(concurrency_level)
    ]
    
    # 使用 gather 等待本轮所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

async def performance_test_client():
    # 配置
    base_url = "http://localhost:11996"  # 根据实际服务地址修改
    speaker = "67a0410a81974dbb94a51c211aee2499"  # 根据实际可用角色名修改
    input_file = "lines.txt"
    output_dir = "tts_100_rounds_test_output"
    concurrency_level = 10  # 每轮并发数
    total_rounds = 100  # 总轮数
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 读取文本行
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    if not lines:
        print("No valid lines found in input file")
        return
    
    print(f"Starting performance test: {total_rounds} rounds, {concurrency_level} concurrent requests per round")
    
    # 总体统计
    total_requests = 0
    total_successful = 0
    total_failed = 0
    total_time_consumed = 0
    round_times = []
    
    # 创建 aiohttp 客户端会话
    async with aiohttp.ClientSession() as session:
        # 记录总体开始时间
        overall_start_time = time.time()
        
        # 执行所有轮次
        for round_id in range(1, total_rounds + 1):
            print(f"\n--- Starting Round {round_id}/{total_rounds} ---")
            
            # 记录本轮开始时间
            round_start_time = time.time()
            
            # 运行本轮测试
            results = await run_test_round(
                session, base_url, lines, speaker, output_dir, round_id, concurrency_level
            )
            
            # 记录本轮结束时间
            round_elapsed_time = time.time() - round_start_time
            round_times.append(round_elapsed_time)
            
            # 统计本轮结果
            round_requests = len(results)
            round_successful = 0
            round_time_sum = 0
            
            for result in results:
                if isinstance(result, Exception):
                    total_failed += 1
                    continue
                    
                total_requests += 1
                round_time_sum += result["elapsed_time"]
                
                if result["success"]:
                    round_successful += 1
                    total_successful += 1
                else:
                    total_failed += 1
            
            print(f"--- Round {round_id} completed in {round_elapsed_time:.2f}s, "
                  f"Success: {round_successful}/{round_requests} ---")
            
            # 累加总时间
            total_time_consumed += round_time_sum
        
        # 计算总体耗时
        overall_elapsed_time = time.time() - overall_start_time
        
        # 输出详细统计信息
        print("\n" + "="*60)
        print("100 ROUNDS PERFORMANCE TEST RESULTS")
        print("="*60)
        print(f"Total rounds: {total_rounds}")
        print(f"Concurrency per round: {concurrency_level}")
        print(f"Total requests: {total_rounds * concurrency_level}")
        print(f"Successful requests: {total_successful}")
        print(f"Failed requests: {total_failed}")
        print(f"Success rate: {(total_successful/(total_rounds * concurrency_level))*100:.2f}%")
        print(f"Overall time taken: {overall_elapsed_time:.2f}s")
        print(f"Average time per request: {total_time_consumed/(total_rounds * concurrency_level):.2f}s")
        if total_successful > 0:
            print(f"Average time for successful requests: {total_time_consumed/total_successful:.2f}s")
        
        # 计算轮次统计
        if round_times:
            avg_round_time = sum(round_times) / len(round_times)
            min_round_time = min(round_times)
            max_round_time = max(round_times)
            print(f"Average time per round: {avg_round_time:.2f}s")
            print(f"Fastest round: {min_round_time:.2f}s")
            print(f"Slowest round: {max_round_time:.2f}s")
        
        print("="*60)

def main():
    # 运行异步性能测试
    asyncio.run(performance_test_client())

if __name__ == "__main__":
    main()