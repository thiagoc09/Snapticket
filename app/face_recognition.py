import boto3
import os

# Configure o cliente AWS Rekognition
rekognition = boto3.client(
    'rekognition',
    region_name='us-east-1',
    aws_access_key_id='AKIAQ3EGR3RLPS2OMU54',
    aws_secret_access_key='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'
)

def compare_faces(source_image_bytes, target_image_bytes):
    response = rekognition.compare_faces(
        SourceImage={'Bytes': source_image_bytes},
        TargetImage={'Bytes': target_image_bytes},
        SimilarityThreshold=80
    )
    return len(response['FaceMatches']) > 0

def load_image_bytes(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()