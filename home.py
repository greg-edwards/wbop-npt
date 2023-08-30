from os import link
import select
import streamlit as st
import folium
from folium.features import Marker, Popup
import pandas as pd
import numpy as np
import geopandas as gpd
import leafmap
import openpyxl

from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.sidebar.image('https://becagroup.sharepoint.com/sites/ClientsandMarkets/Images1/Market%20Profile%20&%20Brand/Beca%20Brand%20&%20Standards/Beca%20Logo%20Black%20PNG.png?csf=1&web=1&e=p6QEq9&cid=d89ac465-29af-4979-83d9-a76c21e84693', width=150, output_format="auto")

st.sidebar.title("About")
st.sidebar.info(
    """
    The Network Prioritisation Tool (NPT) is a Beca-designed tool to help identify and prioritise public transport investment across the Western Bay of Plenty's transport network.
    
    This analysis forms part of a wider programme of work - through the PT Services and Infrastructure Business Case - which is investigating the case for change in the Western Bay of Plenty sub-region’s public transport system  

    """
)

st.sidebar.title("Questions / Contact")
st.sidebar.info(
    """
    If you have any questions/feedback on this app or notice any errors, please contact Greg Edwards (greg.edwards@beca.com)
    """
)

tab1, tab2, tab3 = st.tabs(["Background", "The tool", "How it works"])

with tab1:

    st.title("Western Bay of Plenty")
    st.header("Network Prioritisation Tool")
    st.markdown("""          
                
                **Background:** Depending on the level of investment, there are possibly many hundreds of locations across the Western Bay of Plenty that could warrant and accommodate some level of public transport (PT) investment. This brings with it many challenges in targeting investment in a planned and efficient way.  

                The Network Prioritisation Tool (NPT) has been developed to help identify network locations that could benefit from PT investment. It provides a summary of roads and intersections across the transport network representing varying levels of priority based on specific criteria such as bus delay and forecast passenger demand. Users can customize the analysis for their specific purpose to better understand the factors that influence where investment could be targeted.
                
                Locations are split into several categories:
                - **Key locations:** representing the highest priority locations where sigificant bus delays, bus volumes, and passenger demand is expected.
                - **Delay:** secondary locations outside of the key locations where buses are expected to suffer reasonable levels of delay in the future.
                - **Demand:** secondary locations outside of the key locations experiencing greater levels of bus demand.
                - **All locations:** All of the above.
                
                To view the NPT tool, click on 'The tool' tab above.
                """)

    st.info("For further information on how this tool was developed, click on the 'How it works' tab above.")

with tab2:

    #cache data
    @st.cache_data
    def gdf_load_data(url):
        gdf = gpd.read_file(url)
        return gdf

    @st.cache_data
    def df_load_data(url):
        df = pd.read_excel(url)
        return df

    #import intersection and links data

    intersection_key_locations = gdf_load_data(r"data/key_locations.geojson")
    intersection_delay = gdf_load_data(r"data/delay.geojson")
    intersection_demand = gdf_load_data(r"data/demand.geojson")

    links_key_locations = gdf_load_data(r'data/links_key_locations.geojson')
    links_delay = gdf_load_data(r'data/links_delay.geojson')
    links_demand = gdf_load_data(r'data/links_demand.geojson')

    merged_intersections = df_load_data(r'data/merged_intersections.xlsx')
    merged_links = df_load_data(r'data/merged_links.xlsx')

    #drop-down box
    analysis_selection = st.selectbox('Please select what type of analysis you are interested in exploring.', ['Key locations', 'Delay', 'Demand', 'All locations'])
    
    if analysis_selection == True:
        
        #radio button
        data_selection = st.radio('What type of data do you want to see?', ['Select', 'Roads', 'Intersections', 'Both roads and intersections'])
        

        st.info("Tip: click on the roads or intersections to explore the data further.")

        #define columns
        col1, col2 = st.columns([3, 1])

        #show specific maps and data on selection
        if analysis_selection == 'Key locations' and data_selection == 'Roads':
                
            with col1:
                
                map = links_key_locations.explore(tiles='CartoDB positron',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Critical locations",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(links_key_locations)  
                
            with col2:
                st.subheader("Key Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(links_key_locations.index)}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{links_key_locations['ADT_PT'].mean().astype('int')}** bus users per day (2048).
                            - an average of **{links_key_locations['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_key_locations['LOS'].mean().astype('int')}**, equating to >120 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'Key locations' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_key_locations.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Critical locations",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7
                    })


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(intersection_key_locations)  
                
            with col2:
                st.subheader("Key Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_key_locations.index)}** {data_selection} identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{intersection_key_locations['ADT_PT'].mean().astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{intersection_key_locations['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{intersection_key_locations['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'Key locations' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = intersection_key_locations.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Critical locations",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7})
                
                links_key_locations.explore(
                    m=map,
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Critical locations",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([intersection_key_locations, links_key_locations]))  
                
            with col2:
                st.subheader("Key Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_key_locations.index)}** intersections and **{len(links_key_locations.index)}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{intersection_key_locations['ADT_PT'].mean().astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{intersection_key_locations['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{intersection_key_locations['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """)

        if analysis_selection == 'Delay' and data_selection == 'Roads':
                
            with col1:
                
                map = links_delay.explore(tiles='CartoDB positron',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by delay",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(links_delay)  
                
            with col2:
                st.subheader("Delay Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(links_delay.index)}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{links_delay['ADT_PT'].mean().astype('int')}** bus users per day (2048).
                            - an average of **{links_delay['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_delay['LOS'].mean().astype('int')}**, equating to >80 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'Delay' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_delay.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by delay",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7
                    })


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(intersection_delay)  
                
            with col2:
                st.subheader("Delay Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_delay.index)}** {data_selection} identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{intersection_delay['ADT_PT'].mean().astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{intersection_delay['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{intersection_delay['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'Delay' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = intersection_delay.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by delay",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7})
                
                links_delay.explore(
                    m=map,
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by delay",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([intersection_delay, intersection_demand]))  
                
            with col2:
                st.subheader("Delay Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_delay.index)}** intersections and **{len(links_delay.index)}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{(links_delay['ADT_PT'].mean().astype('int'))+(intersection_delay['ADT_PT'].mean().astype('int'))}** bus users travelling through them every day (2048).
                            - an average of **{(intersection_delay['AM_PT'].mean().astype('int'))+(links_delay['AM_PT'].mean().astype('int'))}** bus users in the AM peak (2048).
                            - average delays of **{intersection_delay['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 
                
        if analysis_selection == 'Demand' and data_selection == 'Roads':
                
            with col1:
                
                map = links_demand.explore(tiles='CartoDB positron',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by demand",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(links_demand)  
                
            with col2:
                st.subheader("Demand Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(links_demand.index)}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{links_demand['ADT_PT'].mean().astype('int')}** bus users per day (2048).
                            - an average of **{links_demand['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_demand['LOS'].mean().astype('int')}**, equating to >80 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'Demand' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_demand.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by demand",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7
                    })


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(intersection_demand)  
                
            with col2:
                st.subheader("Demand Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_demand.index)}** {data_selection} identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{intersection_demand['ADT_PT'].mean().astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{intersection_demand['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{intersection_demand['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'Demand' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = intersection_demand.explore(tiles='CartoDB positron',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by demand",
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"red",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7})
                
                links_demand.explore(
                    m=map,
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by demand",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([links_demand, intersection_demand]))  
                
            with col2:
                st.subheader("Demand Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_demand.index)}** intersections and **{len(links_demand.index)}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{(links_demand['ADT_PT'].mean().astype('int'))+(intersection_demand['ADT_PT'].mean().astype('int'))}** bus users travelling through them every day (2048).
                            - an average of **{(intersection_demand['AM_PT'].mean().astype('int'))+(links_demand['AM_PT'].mean().astype('int'))}** bus users in the AM peak (2048).
                            - average delays of **{intersection_demand['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """)

        if analysis_selection == 'All locations' and data_selection == 'Roads':
                
            with col1:
                                    
                map = links_demand.explore(tiles='CartoDB positron',
                    legend=True,
                    column='LOS',
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by demand",
                    style_kwds= {
                        
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Level of service",
                        "fmt":"{:.0f}",
                    })
                
                links_key_locations.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Key locations",
                    style_kwds= {
                        
                        "weight":3,
                        "opacity":0.7})
                
                links_delay.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by delay",
                    style_kwds= {
                        
                        "weight":3,
                        "opacity":0.7})
                
                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([links_key_locations, links_demand, links_delay]))  
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(links_demand.index))+(len(links_key_locations.index))+(len(links_delay.index))}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{((links_demand['ADT_PT'].mean())+(links_key_locations['ADT_PT'].mean())+(links_delay['ADT_PT'].mean())).astype('int')}** bus users per day (2048).
                            - an average of **{((links_demand['AM_PT'].mean())+(links_key_locations['AM_PT'].mean())+(links_delay['AM_PT'].mean())).astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_key_locations['LOS'].mean().astype('int')}**, equating to >120 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'All locations' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_demand.explore(tiles='CartoDB positron',
                    legend=True,
                    column='DELAY_WAVG',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by demand",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Seconds of delay/hr per bus movement",
                        "fmt":"{:.0f}"})
                
                intersection_key_locations.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Key locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                intersection_delay.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by delay",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([intersection_key_locations, intersection_delay, intersection_demand]))  
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(intersection_demand.index))+(len(intersection_key_locations.index))+(len(intersection_delay.index))}** identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{((intersection_demand['ADT_PT'].mean())+(intersection_key_locations['ADT_PT'].mean())+(intersection_delay['ADT_PT'].mean())).astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{((intersection_demand['AM_PT'].mean())+(intersection_key_locations['AM_PT'].mean())+(intersection_delay['AM_PT'].mean())).astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{((intersection_demand['DELAY_WAVG'].mean())+(intersection_key_locations['DELAY_WAVG'].mean())+(intersection_delay['DELAY_WAVG'].mean())).astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'All locations' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = links_demand.explore(tiles='CartoDB positron',
                    legend=True,
                    column='LOS',
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by demand",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Links - Level of service",
                        "fmt":"{:.0f}",
                    })
                
                links_key_locations.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Key locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                links_delay.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    popup=['LOS', 'ADT_PT', 'AM_PT', 'line_name', 'vehicle_co'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Prioritised by delay",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                intersection_demand.explore(
                    m=map,
                    legend=True,
                    column='DELAY_WAVG',
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by demand",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Intersections - Seconds of delay/hr per bus movement",
                        "fmt":"{:.0f}",
                    })
                
                intersection_key_locations.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Key locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                intersection_delay.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    popup=['AM_PT', 'ADT_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Prioritised by delay",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})

                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                if st.checkbox('Show raw data'):
                    st.subheader('Raw data')
                    st.write(pd.concat([intersection_key_locations, intersection_delay, intersection_demand, links_key_locations, links_demand, links_delay]))  
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(links_demand.index))+(len(links_key_locations.index))+(len(links_delay.index))}** intersections and **{(len(intersection_demand.index))+(len(intersection_key_locations.index))+(len(intersection_delay.index))}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{(((links_demand['ADT_PT'].mean())+(links_key_locations['ADT_PT'].mean())+(links_delay['ADT_PT'].mean())).astype('int'))+(((intersection_demand['ADT_PT'].mean())+(intersection_key_locations['ADT_PT'].mean())+(intersection_delay['ADT_PT'].mean())).astype('int'))}** bus users travelling through them every day (2048).
                            - an average of **{(((links_demand['AM_PT'].mean())+(links_key_locations['AM_PT'].mean())+(links_delay['AM_PT'].mean())).astype('int'))+(((intersection_demand['AM_PT'].mean())+(intersection_key_locations['AM_PT'].mean())+(intersection_delay['AM_PT'].mean())).astype('int'))}** bus users in the AM peak (2048).
                            - average delays of **{((intersection_demand['DELAY_WAVG'].mean())+(intersection_key_locations['DELAY_WAVG'].mean())+(intersection_delay['DELAY_WAVG'].mean())).astype('int')}** seconds every hour per bus movement (2048).
                            
                            """)

    with tab3:
        st.markdown("""
                    
                    The NPT has been developed in a top-down process using a transparent methodology and consistent datasets, transport modelling data, alongside local knowledge and expertise. It is built upon several key information/data sources, such as the Tauranga Transport Strategic Model (TTSM), as well as open source public data. 
                    
                    """)
        st.subheader("Data")

        st.markdown("""
                    
                    OpenStreetMap (OSM) data was downloaded in bulk and used to define road type and other features. This information was combined with geometric outputs from Remix to only identify road segments where services will operate. Several ‘filters’ were defined  and applied to the dataset to help identify road network geometries amenable to investment. The main criteria used included:
                    - Geometric space able to accommodate infrastructure prioritisation measures (i.e., measured by the number of lanes of traffic lanes available in one direction);
                    - The frequency of bus services using road network segment, with higher priority given to network segments that accommodate higher frequency services;
                    - Forecast passenger demand by each network segment, with higher priority given to network segments that accommodate higher passenger demand;
                    - Forecast (2048) delay to buses, with high priority given to locations that experience greater levels of delay;

                    The table below outlines the data inputs into the NPT tool.
                    
                    """)
        table = {'Criteria' : ['Geometric space', 'Service frequency', 'Passenger demand', 'Bus delay'],
                'Data input' : ['Number of general traffic lanes available in one direction (minimum 1+)', 'Remix model data. Network route segments weighted by Hybrid Model network frequency', 'TTSM daily PT trips and AM peak dail trips by network link', 'TTSM 2048 level of service delay by link and node']}

        df = pd.DataFrame(data=table)

        st.table(df)

        st.subheader("Analysis Thresholds")

        st.markdown("""
                    
                    The NPT uses several threshold criteria to identify and prioritise nodes and links:

                    **Key Locations**
                    - Nodes: locations where there is high PT demand (ie equating to roughly 150+ daily trips in AM peak) leading to intersections with forecast high levels of delay (ie, LOS D-F). Nodes ranked by the level of forecast demand (AM peak).
                    - Links: routes/links where there is high PT demand (roughly 150+ daily PT trips in AM peak) and high number of buses (>= 20 per day) under the Hybrid network along low LOS links (ie LOS D-F). Links ranked by the level of forecast demand (AM peak).

                    **Delay Locations**
                    - Nodes: locations (outsie of key locations) where there is high PT demand (ie equating to roughly 150+ daily trips in AM peak) leading to intersections with forecast moderate levels of delay (ie, LOS C-F). Nodes ranked by delay.
                    - Links: routes/links where there is high PT demand (roughly 150+ daily PT trips in AM peak) and high number of buses (>= 20 per day) under the Hybrid network along low LOS links (ie LOS C-F). Links ranked by delay.

                    **Demand Locations**
                    - Nodes: locations (outsie of key locations) where there is moderate PT demand (ie equating to roughly 80+ daily trips in AM peak) leading to intersections with forecast moderate levels of delay (ie, LOS C-F). Nodes ranked by forecast AM peak demand.
                    - Links: routes/links where there is mdoerate PT demand (roughly 80+ daily PT trips in AM peak) and high number of buses (>= 20 per day) under the Hybrid network along low LOS links (ie LOS C-F). Links ranked by forecast AM peak demand. 

                    """)