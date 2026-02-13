import streamlit as st
import yaml
import io

# 1. Load Configuration
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# 2. App Header
st.title(config['app_title'])
st.write(config['app_description'])

# 3. Dynamic Form Generation
st.sidebar.header("Component Features")
user_selections = {}

# Iterate through features defined in YAML and create widgets
for feature in config['features']:
    f_id = feature['id']
    f_label = feature['label']
    f_type = feature['type']
    
    if f_type == 'selectbox':
        user_selections[f_id] = st.sidebar.selectbox(f_label, feature['options'])
        
    elif f_type == 'radio':
        user_selections[f_id] = st.sidebar.radio(f_label, feature['options'])
        
    elif f_type == 'multiselect':
        user_selections[f_id] = st.sidebar.multiselect(f_label, feature['options'])
        
    elif f_type == 'slider':
        user_selections[f_id] = st.sidebar.slider(
            f_label, 
            min_value=feature.get('min', 0), 
            max_value=feature.get('max', 100), 
            value=feature.get('default', 0),
            step=feature.get('step', 1)
        )
        
    elif f_type == 'checkbox':
        user_selections[f_id] = st.sidebar.checkbox(f_label, value=feature.get('default', False))

# 4. NC Program Generator Logic
def generate_nc_code(selections):
    """
    This function simulates creating an NC program.
    Replace the logic below with your actual G-code generation logic.
    """
    buffer = io.StringIO()
    
    # Header
    buffer.write("%\n")
    buffer.write(f"O1001 ({selections.get('material', 'UNK')} PART)\n")
    
    if selections.get('comments'):
        buffer.write(f"(STOCK DIAMETER: {selections.get('diameter')}mm)\n")
        buffer.write(f"(COOLANT: {selections.get('coolant')})\n")
    
    buffer.write("G21 G40 G80 G90\n") # Safety line
    buffer.write("G28 U0 W0\n")       # Home
    
    # Coolant Logic
    coolant_map = {"Flood": "M08", "Mist": "M07", "Through-Spindle": "M88", "Off": "M09"}
    c_code = coolant_map.get(selections.get('coolant'), "M09")
    buffer.write(f"{c_code}\n")
    
    # Operations Logic
    ops = selections.get('operations', [])
    if "Face" in ops:
        buffer.write("(OP: FACING)\nG00 X{0} Z5.0\n...\n".format(selections.get('diameter') + 5))
    if "Drill Center" in ops:
        buffer.write("(OP: DRILLING)\nT0202\n...\n")
        
    buffer.write("M30\n")
    buffer.write("%\n")
    
    return buffer.getvalue()

# 5. Display & Download
st.subheader("Preview Selection")
st.json(user_selections)

if st.button("Generate NC Program"):
    nc_content = generate_nc_code(user_selections)
    
    # Show preview of code
    st.text_area("NC Code Preview", nc_content, height=200)
    
    # Create download button
    st.download_button(
        label="Download .NC File",
        data=nc_content,
        file_name="program.nc",
        mime="text/plain"
    )
