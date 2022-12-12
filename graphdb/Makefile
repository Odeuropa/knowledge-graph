VERSION=10.1.1

free:
	docker build --no-cache --pull --build-arg edition= --build-arg version=${VERSION} -t ontotext/graphdb:${VERSION} graphdb

ee:
	docker build --no-cache --pull --build-arg edition=ee --build-arg version=${VERSION} -t ontotext/graphdb:${VERSION}-ee .

se:
	docker build --no-cache --pull --build-arg edition=se --build-arg version=${VERSION} -t ontotext/graphdb:${VERSION}-se .

ee-upload: ee
	docker push ontotext/graphdb:${VERSION}-ee

se-upload: se
	docker push ontotext/graphdb:${VERSION}-se
