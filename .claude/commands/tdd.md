<tests>
1.    Name the Test you want here
2.    Test you want here
3.    etc etc </tests>
<implementation›
1.    I need a new API endpoint that uploads images to a S3 bucket
2.    Those images are then stored in a new table called images with a reference to their owner
"User"
1.    I want to validate images are no larger than 5mb in size
2.    We need an api to return all images a user has registered to them
3.    We need an api to also delete an image.
‹/implementation›
crules>
Since we are dealing with external services you'll need to mock connections to ANS
The main functionality I want tested is image validate, and api payloads matching what they should. </rules>