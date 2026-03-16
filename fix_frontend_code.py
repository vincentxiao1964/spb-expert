
import os

# Fix order_list.vue
order_list_path = r"d:\spb-expert11\frontend\src\pages\merchant\order_list.vue"
try:
    with open(order_list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Identify the closing </view> of container and move the modal inside
    if '<!-- Ship Modal -->' in content and '</view>\n\n        <!-- Ship Modal -->' in content:
        # Simple string manipulation might be risky if indentation varies, but let's try
        # Move the modal block inside the last view
        parts = content.split('</view>\n\n        <!-- Ship Modal -->')
        if len(parts) == 2:
            main_part = parts[0]
            modal_part = '        <!-- Ship Modal -->' + parts[1].split('</template>')[0]
            new_content = main_part + '\n' + modal_part + '    </view>\n</template>\n' + parts[1].split('</template>')[1]
            
            # This is getting messy. Let's do a simpler replacement.
            # We know the structure from the read.
            pass

    # Alternative: Read all lines, find the last </view> before </template>, insert modal before it.
    lines = content.splitlines()
    modal_start_idx = -1
    container_end_idx = -1
    
    for i, line in enumerate(lines):
        if '<!-- Ship Modal -->' in line:
            modal_start_idx = i
        if '</template>' in line:
            # Find the </view> before this
            for j in range(i-1, -1, -1):
                if '</view>' in lines[j]:
                    container_end_idx = j
                    break
            break
            
    if modal_start_idx > -1 and container_end_idx > -1 and modal_start_idx > container_end_idx:
        modal_lines = lines[modal_start_idx:len(lines)-2] # Exclude </template> and last empty line if any
        # Actually, let's just grab everything from modal_start_idx to the line before </template>
        
        # Locate </template>
        template_end_idx = -1
        for i in range(len(lines)-1, -1, -1):
            if '</template>' in lines[i]:
                template_end_idx = i
                break
        
        if template_end_idx > modal_start_idx:
            modal_block = lines[modal_start_idx:template_end_idx]
            
            # Remove modal block from original location
            # And insert it before container_end_idx
            
            # Reconstruct
            new_lines = lines[:container_end_idx] + modal_block + lines[container_end_idx:modal_start_idx] + lines[template_end_idx:]
            # Note: lines[container_end_idx:modal_start_idx] includes the </view> of container and any empty lines.
            
            # Actually:
            # 1. Everything up to container_end_idx (exclusive)
            # 2. Modal block
            # 3. The container closing tag (lines[container_end_idx])
            # 4. Everything after the original modal block (which is effectively empty/closing template)
            
            # Wait, the modal block is AFTER container closing tag currently.
            # Original:
            # ... content ...
            # </view>  <-- container_end_idx
            #
            # <!-- Ship Modal --> <-- modal_start_idx
            # ...
            # </view>
            #
            # </template>
            
            # Desired:
            # ... content ...
            # <!-- Ship Modal -->
            # ...
            # </view>
            # </view> <-- container_end_idx (moved down)
            
            # Simpler:
            # 1. Extract modal block text.
            # 2. Replace original modal block with empty string.
            # 3. Replace '</view>' (last one before modal) with 'MODAL_BLOCK\n</view>'
            
            full_text = '\n'.join(lines)
            modal_text = '\n'.join(modal_block)
            
            # Remove modal text from bottom
            text_without_modal = full_text.replace(modal_text, '')
            
            # Find the last </view> inside the template (which is now text_without_modal)
            # It should be the one closing container.
            # Be careful not to match inner views.
            # The container is indentation level 1 (tab).
            # line 34: "	</view>" (tab + </view>)
            
            # Let's just do a direct string replacement as I saw in the file content.
            # "	</view>\n\n        <!-- Ship Modal -->" -> "\n        <!-- Ship Modal --> ... </view>"
            
            # Actually, I can just read the file, verify the string I want to replace, and replace it.
            # The file content showed:
            # 34->	</view>
            # 35->
            # 36->        <!-- Ship Modal -->
            
            # So replace "	</view>\n\n        <!-- Ship Modal -->" with "        <!-- Ship Modal -->"
            # AND append "	</view>" at the end of the modal block?
            # No, the modal block ends with "</view>".
            # So I need to wrap the modal block inside the container.
            
            # Let's try to rewrite the file completely with correct structure.
            pass

    # Let's use a simpler approach: Read file, fix specific issue.
    # The issue is "Component template should contain exactly one root element".
    # I will wrap the entire template content in a new <view>.
    
    # Read again
    with open(order_list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find <template> and </template>
    start = -1
    end = -1
    for i, line in enumerate(lines):
        if '<template>' in line:
            start = i
        if '</template>' in line:
            end = i
            
    if start != -1 and end != -1:
        # Insert <view> after <template>
        lines.insert(start + 1, '    <view>\n')
        # Insert </view> before </template>
        lines.insert(end + 1, '    </view>\n')
        
        with open(order_list_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Fixed {order_list_path}")
except Exception as e:
    print(f"Error fixing order_list.vue: {e}")

# Fix detail.vue
detail_path = r"d:\spb-expert11\frontend\src\pages\procurement\detail.vue"
try:
    with open(detail_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace("e.data?.detail", "(e.data && e.data.detail)")
    
    if new_content != content:
        with open(detail_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {detail_path}")
    else:
        print("detail.vue already fixed or pattern not found")

except Exception as e:
    print(f"Error fixing detail.vue: {e}")

