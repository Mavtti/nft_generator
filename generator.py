import ipaddress
from IPython.display import display 
from PIL import Image
import ipfshttpclient
import random
import json
from pathlib import Path
import os

os.system('cls' if os.name=='nt' else 'clear')

def create_new_image(all_images, config):
    new_image = {}
    for layer in config["layers"]:
      if layer["name"] == "bras":
        values = []
        for v in layer["values"]:
            if new_image["corps"].split("_")[0] == v.split("_")[0]:
                values.append(v)
        weights = [100/len(values) for _ in values]
      else:
        values = layer["values"]
        weights = layer["weights"]
      new_image[layer["name"]] = random.choices(values, weights)[0]
        
    for incomp in config.get("incompatibilities", []):
      for attr in new_image:
        if new_image[incomp["layer"]] == incomp["value"] and new_image[attr] in incomp["incompatible_with"]:
          return create_new_image(all_images, config)

    if new_image in all_images:
      return create_new_image(all_images, config)
    else:
      return new_image

def generate_unique_images(amount, config):
  print("Generating {} unique NFTs...".format(amount))
  # import ipdb; ipdb.set_trace()
  pad_amount = len(str(amount))
  trait_files = {}
  config["layers"].sort(key=lambda k : k['order'])

  for trait in config["layers"]:
    trait_files[trait["name"]] = {}
    for x, key in enumerate(trait["values"]):
      trait_files[trait["name"]][key] = trait["filename"][x]


  all_images = []
  for i in range(amount): 
    new_trait_image = create_new_image(all_images, config)
    all_images.append(new_trait_image)

  i = 1
  for item in all_images:
      item["tokenId"] = i
      i += 1

  for i, token in enumerate(all_images):
    attributes = []
    for key in token:
      if key != "tokenId":
        attributes.append({"trait_type": key, "value": token[key]})
    token_metadata = {
        "image": config["baseURI"] + "/images/" + str(token["tokenId"]) + '.png',
        "tokenId": token["tokenId"],
        "name":  config["name"] + str(token["tokenId"]).zfill(pad_amount),
        "description": config["description"],
        "attributes": attributes
    }
    with open('./metadata/' + str(token["tokenId"]) + '.json', 'w') as outfile:
        json.dump(token_metadata, outfile, indent=4)

  with open('./metadata/all-objects.json', 'w') as outfile:
    json.dump(all_images, outfile, indent=4)
  
  for item in all_images:
    layers = []
    for index, attr in enumerate(item):
      if attr != 'tokenId':
        layers.append([])
        layers[index] = Image.open(
            f"{config['layers'][index]['trait_path']}/{trait_files[attr][item[attr]]}.png"
        ).convert('RGBA')

    if len(layers) == 1:
      rgb_im = layers[0].convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      rgb_im.save("./results/" + file_name)
    elif len(layers) == 2:
      main_composite = Image.alpha_composite(layers[0], layers[1])
      rgb_im = main_composite.convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      rgb_im.save("./results/" + file_name)
    elif len(layers) >= 3:
      main_composite = Image.alpha_composite(layers[0], layers[1])
      layers.pop(0)
      layers.pop(0)
      for index, remaining in enumerate(layers):
        main_composite = Image.alpha_composite(main_composite, remaining)
      rgb_im = main_composite.convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      Path(f"./results").mkdir(parents=True, exist_ok=True)
      rgb_im.save(f"./results/" + file_name)
  
  with ipfshttpclient.connect() as client:
    ipfs_hash = client.add('results', recursive=True)

  cid = "ipfs://{}".format(cid)
  for image_ipfs in ipfs_hash:
    if '.png' in image_ipfs["Name"]:
      tokenID = image_ipfs['Name'].replace("results/", "")[:-4]
      with open(f"./metadata/{tokenID}.json", "w") as infile:
        original_json = json.loads(infile.read())
        original_json["image"] = original_json["image"].replace(config["baseURI"]+"/", cid+"/")
        json.dump(original_json, outfile, indent=4)
  
  with ipfshttpclient.connect() as client:
    ipfs_hash = client.add('metadata', recursive=True)



generate_unique_images(1000, {
  "layers": 
    [
      {
	    "order": int(p.replace('./images/', '')[:2]),
        "name": p.replace('./images/', '')[3:],
        "values": [f.replace('.png', '') for f in files],
        "trait_path": p,
        "filename": [f.replace('.png', '') for f in files],
        "weights": [100/len(files) for _ in files]
      }
      for p,d,files in os.walk('./images/') if not d
    ],
  "baseURI": ".",
  "name": "NFT #",
  "description": "This is a description for this NFT series."
})
