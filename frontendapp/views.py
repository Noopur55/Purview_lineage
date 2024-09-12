from django.shortcuts import render, HttpResponse, redirect
from pyapacheatlas.auth import ServicePrincipalAuthentication
from pyapacheatlas.core import (
    PurviewClient,
    AtlasEntity,
    AtlasProcess,
    TypeCategory,
    AtlasAttributeDef,
    AtlasClient,
)
from azure.purview.scanning import PurviewScanningClient
from pyapacheatlas.core.collections import PurviewCollectionsClient
from dotenv import load_dotenv
import os
import hashlib
import json
import requests
from rest_framework import viewsets
from azure.identity import ClientSecretCredential
from .models import onboarding_system, onboarding_applications
from rest_framework.decorators import api_view


load_dotenv()


##authentication to purview
def authentocation():
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")
    tenant_id = os.getenv("tenant_id")

    auth = ServicePrincipalAuthentication(tenant_id, client_id, client_secret)
    purview_account_name = "purview-p"
    purview_client = PurviewClient(
        account_name=purview_account_name, authentication=auth
    )
    return (
        client_id,
        client_secret,
        auth,
        purview_account_name,
        purview_client,
        tenant_id,
    )


# onboarding page to onboard system here ad save to database.


def onboarding_application(request):
    try:
        if request.method == "POST":
            print(request.POST)
            oar_id = request.POST.get("oarid")
            oar_status = request.POST.get("oarstatus")
            # team = request.POST.get('team')
            ucid = request.POST.get("ucid")
            ucowner = request.POST.get("ucowner")
            grid_owner = request.POST.get("gowner")
            product_owner = request.POST.get("po")
            cntct = request.POST.get("cntct")
            is_goldersource = request.POST.get("goldersource") == "yes"
            is_datatodial = request.POST.get("datatodial") == "yes"

            onboarding_app = onboarding_system(
                OAR_Id=oar_id,
                Usecase_Id=ucid,
                Usecase_Owner=ucowner,
                Oar_Status=oar_status,
                Grid_Owner=grid_owner,
                Product_Owner=product_owner,
                Dedicated_Contact=cntct,
                is_Golden_Source=is_goldersource,
                Is_Data_Sending_to_DIAL=is_datatodial,
            )
            onboarding_app.save()
            print(onboarding_app)
            return redirect("application")
        context = {}
        return render(request, "onboarding_usecase.html", context)
    # return HttpResponse("Application submitted successfully")

    except Exception as e:
        print("Exception:", e)
        return HttpResponse("make sure you are not entering a duplicate entry.")


# application onboard page
def application(request):
    try:
        if request.method == "POST":
            print(request.POST)

            services = request.POST.get("azures")
            solution_intent_link = request.POST.get("solintent")
            getting_data_from_OAR = request.POST.get("oardatafrom")
            sending_data_to_OAR = request.POST.get("oardatato")
            environment = request.POST.get("envs")
            data_hop_layers = request.POST.get("hoplayer")
            #final_data_zone = request.POST.get("finallayer")
            target_completion_sprint = request.POST.get("completiondate")

            onboard_each_app = onboarding_applications(
                Services=services,
                Solution_Intent_Link=solution_intent_link,
                Getting_Data_From_OAR=getting_data_from_OAR,
                Sending_Data_To_OAR=sending_data_to_OAR,
                Environment=environment,
                Data_Hop_Layers=data_hop_layers,
                #Final_Data_Zone=final_data_zone,
                Target_Completion_Sprint=target_completion_sprint,
            )
            onboard_each_app.save()
            print(onboard_each_app)
            return redirect("save_collection")
        context = {}
        return render(request, "index.html", context)
    # return HttpResponse("Application submitted successfully")

    except Exception as e:
        print("Exception:", e)
        return HttpResponse("Make sure everything entering as per database schema")


# page to create collection
def secret_page(request):
    context = {}
    return render(request, "save_collection.html", context)


# saving collection in purview
def save_collection_to_purview(request):
    if request.method == "POST":
        collection_to_save = request.POST.get("collectionname")
        parent_collection_name = request.POST.get("parentcollectionname")
        print("paremt collection :", parent_collection_name)
        (
            client_id,
            client_secret,
            auth,
            purview_account_name,
            purview_client,
            tenant_id,
        ) = authentocation()
        # print("here in collection view:", client_id, client_secret, auth, purview_account_name, purview_client)
        all_collections = [l for l in purview_client.collections.list_collections()]

        match_found_parent = any(
            collection_name["friendlyName"] == parent_collection_name
            for collection_name in all_collections
        )
        parent_name = [
            collection_name["friendlyName"]
            for collection_name in all_collections
            if collection_name["friendlyName"] == parent_collection_name
        ]

        # referencename = [collection_name for collection_name in all_collections if collection_name.get('parentCollection',{}).get('referenceName')==parent_name[0]]
        # print(referencename)
        match_found_savecollection = any(
            collection_name["friendlyName"] == collection_to_save
            and collection_name.get("parentCollection", {}).get("referenceName")
            != parent_name[0]
            for collection_name in all_collections
        )
        if match_found_parent and not match_found_savecollection:
            parent_collection_id = get_collection_id(
                all_collections, parent_collection_name
            )
            hashed_string = hashlib.sha256(collection_to_save.encode()).hexdigest()
            short_id = hashed_string[:6]

            create_resp = purview_client.collections.create_or_update_collection(
                name=short_id,
                friendlyName=collection_to_save,
                parentCollectionName=parent_collection_id,
            )

            print(create_resp)

            # context={'collection_role_assignment':collection_to_save,
            #                 'tenant_id':tenant_id}
            values = {
                "collection_role_assignment": collection_to_save,
                "id": short_id,
                "tenant_id": tenant_id,
            }
            request.session.update(values)
            context = values

            return render(request, "role_assignments.html", context=context)
        elif match_found_savecollection:
            context = {
                "parent_collection_name": parent_collection_name,
                "collection_to_save": collection_to_save,
            }
            return render(request, "auth/collection_name_exist.html", context=context)
        else:
            context = {"parent_collection_name": parent_collection_name}
            return render(
                request, "auth/collectionnamenotfoundinpurview.html", context=context
            )

        # return render(request, 'collection_role_assignment.html', context=context)


# add collection admin role assignment for the collection created.
def role_assignmentss(request):
    if request.method == "POST":
        agf_id = request.POST.get("objectid")
        print("agf_id is:", agf_id)

        (
            client_id,
            client_secret,
            auth,
            purview_account_name,
            purview_client,
            tenant_id,
        ) = authentocation()
        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        token = credential.get_token("https://purview.azure.net/.default").token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        # 'collection_role_assignment' : collection_to_save,
        #     'id': short_id
        collection_to_save = request.session.get("collection_role_assignment", None)
        short_id = request.session.get("id", None)
        tenant_id = request.session.get("tenant_id", None)

        # print("my collection to save and id is:", collection_to_save," ", short_id)
        apiurl = f"https://{purview_account_name}.purview.azure.com/policystore/collections/{short_id}/metadataPolicy?api-version=2021-07-01"
        response = requests.get(apiurl, headers=headers, verify=False)
        if response.status_code == 200:
            payload = json.loads(response.text)
            print("payload:", payload)
            policy_id = payload["id"]
            some_id = payload["properties"]["attributeRules"][0]["dnfCondition"][0][0][
                "attributeValueIncludedIn"
            ].append(agf_id)

            apiurl = f"https://{purview_account_name}.purview.azure.com/policystore/metadataPolicies/{policy_id}?api-version=2021-07-01"

            response = requests.put(apiurl, headers=headers, json=payload, verify=False)
            print("responsessss:----", response.content)
            if response.status_code == 200:
                data = json.loads(response.text)
                print("your role has been created:", data)
            else:
                print(response.status_code)

        else:
            print(response.status_code)
        context = {"collection_role_assignment": short_id, "tenant_id": tenant_id}
    return render(request, "collection_role_assignment.html", context=context)


# get the collection id which is name in purview entity to execute further .
def get_collection_id(all_collections, collection_name, parent_collection_id=None):
    collection_id = None
    for elem in all_collections:
        if elem["friendlyName"] == collection_name:
            if parent_collection_id is not None:
                if elem["parentCollection"]["referenceName"] == parent_collection_id:
                    collection_id = elem["name"]
                    break
            else:
                collection_id = elem["name"]
                break

    if collection_id is None:
        raise Exception(
            "collection name not found in purview:{}".format(collection_name)
        )

    return collection_id
