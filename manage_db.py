import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import ToolMessage

def list_threads():
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    cursor = conn.cursor()
    
    print("--- Available Threads ---")
    # Checkpoints table usually has columns like thread_id, checkpoint_id, parent_checkpoint_id, type, channel_values, etc.
    # We want to find distinct thread_ids.
    try:
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = cursor.fetchall()
        
        if not threads:
            print("No threads found in database.")
            return []
            
        thread_list = [t[0] for t in threads]
        for tid in thread_list:
            # Count checkpoints for this thread
            cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (tid,))
            count = cursor.fetchone()[0]
            print(f"Thread ID: {tid} (Checkpoints: {count})")
        
        return thread_list
    except Exception as e:
        print(f"Error listing threads: {e}")
        return []
    finally:
        conn.close()

def inspect_thread(thread_id):
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n--- Inspecting Thread: {thread_id} ---")
    
    # Get latest state
    checkpoint = checkpointer.get(config)
    if not checkpoint:
        print("No checkpoint found.")
        return

    print(f"Latest Checkpoint ID: {checkpoint['id']}")
    
    if 'messages' in checkpoint['channel_values']:
        messages = checkpoint['channel_values']['messages']
        print(f"Total Messages: {len(messages)}")
        print("\nMessage History:")
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content = msg.content
            # Truncate content if too long
            if len(str(content)) > 100:
                content = str(content)[:100] + "..."
            
            print(f"[{i}] {msg_type}: {content}")
            
            # If it's a ToolMessage, print more details
            if isinstance(msg, ToolMessage):
                print(f"    Tool Call ID: {msg.tool_call_id}")
                print(f"    Artifact: {msg.artifact}")
    else:
        print("No 'messages' key in channel_values.")

if __name__ == "__main__":
    import sys
    # Redirect stdout to a file
    with open("db_output_utf8.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        threads = list_threads()
        if threads:
            target_thread = "1"
            if target_thread not in threads:
                target_thread = threads[0]
            
            inspect_thread(target_thread)
