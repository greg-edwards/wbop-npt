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
    
    This analysis forms part of a wider programme of work - through the PT Services and Infrastructure Business Case - which is investigating the case for change in the Western Bay of Plenty sub-region’s public transport system.  

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
                - **Priority Locations:** representing the highest priority locations where sigificant bus delay, bus volume, and passenger demand are expected.
                - **Secondary Locations:** representing less critical locations outside of the Tauriko-Arataki (T2A) Primary Corridor where buses are expected to suffer moderate levels of delay and there is moderate levels of bus demand.
                - **All locations:** All of the above.
                
                To view the NPT tool, click on 'The tool' tab above.
                """)

    st.info("For further information on how this tool was developed, click on the 'How it works' tab.")

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

    intersection_key_locations = gdf_load_data(r"data/intersections_key_locations.geojson")
    intersection_secondary = gdf_load_data(r"data/intersections_outside_primary.geojson")

    links_key_locations = gdf_load_data(r'data/links_key_locations.geojson')
    links_secondary = gdf_load_data(r'data/links_outside_primary.geojson')

    merged_intersections = df_load_data(r'data/merged_intersections.xlsx')
    merged_links = df_load_data(r'data/merged_links.xlsx')

    #drop-down box
    analysis_selection = st.selectbox('Please select what type of analysis you are interested in exploring.', ['Select', 'Priority locations', 'Secondary Locations', 'All locations'])
    
    if analysis_selection == 'Priority locations' or 'Secondary Locations' or 'All locations':
        
        #radio button
        data_selection = st.radio('What type of data do you want to see?', ['Select', 'Roads', 'Intersections', 'Both roads and intersections'])
        
        
        #define columns
        col1, col2 = st.columns([3, 1])

        #show specific maps and data on selection
        if analysis_selection == 'Priority locations' and data_selection == 'Roads':
                
            with col1:
                
                map = links_key_locations.explore(tiles='CartoDB positron',
                    legend=False,
                    tooltip=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    popup=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Priority locations",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                
                st.info("Tip: click on the roads or intersections to explore the data further.")
                    
                
            with col2:
                st.subheader("Priority Locations Summary")

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

        if analysis_selection == 'Priority locations' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_key_locations.explore(tiles='CartoDB positron',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Priority locations",
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
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
                     
                st.info("Tip: click on the roads or intersections to explore the data further.")
                
            with col2:
                st.subheader("Priority Locations Summary")

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


        if analysis_selection == 'Priority locations' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = intersection_key_locations.explore(tiles='CartoDB positron',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Priority locations",
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
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
                    tooltip=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    popup=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Priority locations",
                    style_kwds= {
                        "color":"red",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                
                st.info("Tip: click on the roads or intersections to explore the data further.")    
                
            with col2:
                st.subheader("Priority Locations Summary")

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

        if analysis_selection == 'Secondary Locations' and data_selection == 'Roads':
                
            with col1:
                
                map = links_secondary.explore(tiles='CartoDB positron',
                    legend=False,
                    tooltip=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    popup=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Secondary locations",
                    style_kwds= {
                        "color":"orange",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                
            with col2:
                st.subheader("Secondary Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(links_secondary.index)}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{links_secondary['ADT_PT'].mean().astype('int')}** bus users per day (2048).
                            - an average of **{links_secondary['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_secondary['LOS'].mean().astype('int')}**, equating to >80 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'Secondary Locations' and data_selection == 'Intersections':
                
            with col1:
                
                map = intersection_secondary.explore(tiles='CartoDB positron',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Secondary locations",
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"orange",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7
                    })


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                     
                
            with col2:
                st.subheader("Secondary Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_secondary.index)}** {data_selection} identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{intersection_secondary['ADT_PT'].mean().astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{intersection_secondary['AM_PT'].mean().astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{intersection_secondary['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'Secondary Locations' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                map = intersection_secondary.explore(tiles='CartoDB positron',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    legend=False,
                    zoom_on_click=True,
                    name="Intersections - Secondary locations",
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    marker_type="circle_marker",
                    marker_kwds={
                        "radius" : "6"},
                    style_kwds= {
                        "fillColor":"orange",
                        "stroke":True,
                        "weight":0.6,
                        "opacity":0.7})
                
                links_secondary.explore(
                    m=map,
                    legend=False,
                    tooltip=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    popup=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Secondary locations",
                    style_kwds= {
                        "color":"orange",
                        "weight":3,
                        "opacity":0.7})


                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                     
                
            with col2:
                st.subheader("Secondary Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{len(intersection_secondary.index)}** intersections and **{len(links_secondary.index)}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{(links_secondary['ADT_PT'].mean().astype('int'))+(intersection_secondary['ADT_PT'].mean().astype('int'))}** bus users travelling through them every day (2048).
                            - an average of **{(intersection_secondary['AM_PT'].mean().astype('int'))+(links_secondary['AM_PT'].mean().astype('int'))}** bus users in the AM peak (2048).
                            - average delays of **{intersection_secondary['DELAY_WAVG'].mean().astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 
                
        
        if analysis_selection == 'All locations' and data_selection == 'Roads':
                
            with col1:
                
                st.info("Note: On this map, each link is weighted by the severity of delay (ie LoS).")
                                    
                map = links_key_locations.explore(tiles='CartoDB positron',
                    legend=True,
                    column='LOS',
                    tooltip=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    popup=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Priority locations",
                    style_kwds= {
                        
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Level of service",
                        "fmt":"{:.0f}",
                    })
                
                links_secondary.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    popup=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Secondary locations",
                    style_kwds= {
                        
                        "weight":3,
                        "opacity":0.7})
                
                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                     
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(links_secondary.index))+(len(links_key_locations.index))}** road segments identified in this analysis.

                            These roads have been selected because they are forecast to accomodate:
                            - an average of **{((links_secondary['ADT_PT'].mean())+(links_key_locations['ADT_PT'].mean())).astype('int')}** bus users per day (2048).
                            - an average of **{((links_secondary['AM_PT'].mean())+(links_key_locations['AM_PT'].mean())).astype('int')}** bus users in the AM peak (2048).
                            - average level of service (LoS) classification of **{links_key_locations['LOS'].mean().astype('int')}**, equating to >120 seconds of delay per bus every hour (2048).
                            
                            """)

        if analysis_selection == 'All locations' and data_selection == 'Intersections':
                
            with col1:
                
                st.info("Note: On this map, each intersection is weighted by the severity of delay (ie LoS).")
                
                map = intersection_key_locations.explore(tiles='CartoDB positron',
                    legend=True,
                    column='DELAY_WAVG',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Priority locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Seconds of delay/hr per bus movement",
                        "fmt":"{:.0f}"})
                
                intersection_secondary.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Secondary locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(intersection_secondary.index))+(len(intersection_key_locations.index))}** identified in this analysis.

                            These intersections have been selected because they accomodate::
                            - an average of **{((intersection_secondary['ADT_PT'].mean())+(intersection_key_locations['ADT_PT'].mean())).astype('int')}** bus users travelling through them every day (2048).
                            - an average of **{((intersection_secondary['AM_PT'].mean())+(intersection_key_locations['AM_PT'].mean())).astype('int')}** bus users in the AM peak (2048).
                            - average delays of **{((intersection_secondary['DELAY_WAVG'].mean())+(intersection_key_locations['DELAY_WAVG'].mean())).astype('int')}** seconds every hour per bus movement (2048).
                            
                            """) 


        if analysis_selection == 'All locations' and data_selection == 'Both roads and intersections':
                
            with col1:
                
                st.info("Note: On this map, each intersection and link is weighted by the severity of delay (ie LoS).")
                
                map = links_key_locations.explore(tiles='CartoDB positron',
                    legend=True,
                    column='LOS',
                    tooltip=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    popup=['label', 'ADT_PT', 'AM_PT', 'LOS'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Priority locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Links - Level of service",
                        "fmt":"{:.0f}",
                    })
                
                links_secondary.explore(
                    m=map,
                    column='LOS',
                    legend=False,
                    tooltip=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    popup=['Label', 'ADT_PT', 'AM_PT', 'LOS', 'length'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Links - Secondary locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                              
                intersection_key_locations.explore(
                    m=map,
                    legend=True,
                    column='DELAY_WAVG',
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Priority locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7},
                    legend_kwds= {
                        "caption":"Intersections - Seconds of delay/hr per bus movement",
                        "fmt":"{:.0f}",
                    })
                
                intersection_secondary.explore(
                    m=map,
                    column='DELAY_WAVG',
                    legend=False,
                    tooltip=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    popup=['LABEL', 'ADT_PT', 'AM_PT', 'DELAY_WAVG'],
                    highlight=True,
                    zoom_on_click=True,
                    name="Intersections - Secondary locations",
                    style_kwds= {
                        "weight":3,
                        "opacity":0.7})
                
                folium.LayerControl().add_to(map)
                
                out = st_folium(map, use_container_width=True)
                    
                
            with col2:
                st.subheader("All Locations Summary")

                st.markdown(f"""
                            
                            This shows the results of analysis for:
                            - {analysis_selection}; where,
                            - {data_selection} has been selected.

                            There are **{(len(links_secondary.index))+(len(links_key_locations.index))}** roads and **{(len(intersection_secondary.index))+(len(intersection_key_locations.index))}** road segments identified in this analysis.

                            These roads and intersections have been selected because they accomodate:
                            - an average of **{(((links_secondary['ADT_PT'].mean())+(links_key_locations['ADT_PT'].mean())).astype('int'))+(((intersection_secondary['ADT_PT'].mean())+(intersection_key_locations['ADT_PT'].mean())).astype('int'))}** bus users travelling through them every day (2048).
                            - an average of **{(((links_secondary['AM_PT'].mean())+(links_key_locations['AM_PT'].mean())).astype('int'))+(((intersection_secondary['AM_PT'].mean())+(intersection_key_locations['AM_PT'].mean())).astype('int'))}** bus users in the AM peak (2048).
                            - average delays of **{((intersection_secondary['DELAY_WAVG'].mean())+(intersection_key_locations['DELAY_WAVG'].mean())).astype('int')}** seconds every hour per bus movement (2048).
                            
                            """)

with tab3:
    st.markdown("""
                
                The NPT has been developed in a top-down process using a variety of datasets, including transport modelling data, Remix model outputs, alongside open-source data. It is built upon several key information/data sources, such as the Tauranga Transport Strategic Model (TTSM), as well as General Transit Feed Specification data. 
                
                """)
    st.subheader("Data")

    st.markdown("""
                
                OpenStreetMap (OSM) data was downloaded in bulk and used to define road type and other features. This information was combined with geometric outputs from Remix to only identify road segments where services will operate. Several ‘filters’ were defined  and applied to the dataset to help identify road network geometries amenable to investment. The main criteria used included:
                - The frequency of bus services using road network segment, with higher priority given to network segments that accommodate higher frequency services;
                - Forecast passenger demand (2048) by each network segment, with higher priority given to network segments that accommodate higher passenger demand;
                - Forecast (2048) delay to buses, with high priority given to locations that experience greater levels of delay;

                The table below outlines the data inputs into the NPT tool.
                
                """)
    table = {'Criteria' : ['Service frequency', 'Passenger demand', 'Bus delay'],
            'Data input' : ['Remix model data. Network route segments weighted by Hybrid Model network frequency', 'TTSM daily PT trips and AM peak dail trips by network link', 'TTSM 2048 level of service delay by link and node']}

    df = pd.DataFrame(data=table)
    df.set_index('Criteria')
    
 
    st.table(df)

    st.subheader("Analysis Thresholds")

    st.markdown("""
                
                The NPT uses several threshold criteria to identify and prioritise nodes and links:

                **Priority Locations**
                - Nodes: locations where there is high PT demand (ie equating to roughly 150+ daily trips in AM peak) leading to intersections with forecast high levels of delay (ie, LOS D-F).
                - Links: routes/links where there is high PT demand (roughly 150+ daily PT trips in AM peak) and high number of buses (>= 20 per hour) under the Hybrid network along low LOS links (ie LOS D-F).

                **Secondary Locations (Outside T2A Primary Corridor)**
                - Nodes: locations where there is moderate PT demand (ie equating to roughly 80+ daily trips in AM peak) leading to intersections with moderate levels of delay (ie, LOS C-F).
                - Links: routes/links where there is moderate PT demand (roughly 80+ daily PT trips in AM peak) and high number of buses (>= 20 per hour) under the Hybrid network along low LOS links (ie LOS C-F).

                """)