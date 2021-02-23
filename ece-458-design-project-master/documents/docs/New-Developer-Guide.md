# Frontend Dev Guide

## Overall Architecture

Simply put, it's a standard **React** single page app utilizing **ant design** for the UI elements.

## Codebase

Starting from `src`,

`api` directory contains all the files that contain methods to interact with the server, so that the rest of the codebase is unaware of the actual implementation.

`components` has the usual React elements. _Hooks_ _Hooks_ _Hooks_

`global` has all the global side effects.

## Dev Tools

Running `npm run format` / using `eslint` extension with VS code will lint-beautify the code automatically.

`npm run dev` will put the webpack into watch mode, which will observe changes on the file system and recompile the code automatically.

`npm run build` produces a heavily optimized production build of the app. The compilation is slow, but it's probably for a good reason.

## Relevant links

- https://reactjs.org/docs/hooks-state.html

- https://reacttraining.com/react-router/web/api/HashRouter

- https://react-redux.js.org/introduction/quick-start

- https://ant.design/docs/react/introduce

# Backend Dev Guide

## Overall Architecture

The backend uses Django Rest Framework to manage routes, views, models, users, auth, and everything else.

## Directory Structure

The functionalities of this server are partitioned into various Django apps: the default app (hyposoft), equipment, bulk, changeplan, frontend, hypo_auth, network, power, system_log.

equipment: Deals with the core models of the app.

bulk: Has APIs to import/export models, assets and network connections via csv.

changeplan: Contains logic to deal with changeplan-related functionality.

frontend: contains all of the frontend resources / source files.

hypo_auth: contains all the authentication-related files, including the shibboleth REMOTE_USER integration

network: Deals with network connections between the assets.

power: Deals with power-related logic, including the interface between PDU Networkx 98 Pro.

system_log: contains all the files related to audit logs.

## Tests

There are various tests in `tests.py`. They are automatically run upon pushing code to Gitlab. They test validation logic for the models, such as regex constraints and uniqueness constraints.

## Model Schemas

The model schemas, which describes exactly how data models should be mapped out in a sql databse, are specified in `models.py`.

## API sets

> All APIs are based on the `apis.md` at the parent directory of this file.

The API sets are defined on `urls.py` on each of the "apps". Alternatively, you can run the server locally and point to `localhost:${PORT}/api/` and it'll list out the available API sets.

## Relevant Links

- https://www.django-rest-framework.org/

- https://docs.djangoproject.com/en/3.0/topics/testing/

- https://django-import-export.readthedocs.io/en/latest/
