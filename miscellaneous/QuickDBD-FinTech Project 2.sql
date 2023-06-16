-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/QuiS3k
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "assets" (
    "asset_id" SERIAL   NOT NULL,
    "ticker" VARCHAR(255)   NOT NULL,
    "name" VARCHAR(255)   NOT NULL,
    CONSTRAINT "pk_assets" PRIMARY KEY (
        "asset_id"
     ),
    CONSTRAINT "uc_assets_ticker" UNIQUE (
        "ticker"
    )
);

CREATE TABLE "exchange_connections" (
    "exconn_id" SERIAL   NOT NULL,
    "exchange_id" INT   NOT NULL,
    "user_id" VARCHAR(255)   NOT NULL,
    CONSTRAINT "pk_exchange_connections" PRIMARY KEY (
        "exconn_id"
     )
);

CREATE TABLE "exchanges" (
    "exchange_id" SERIAL   NOT NULL,
    "name" VARCHAR(255)   NOT NULL,
    "address" VARCHAR(255)   NOT NULL,
    "city" VARCHAR(255)   NOT NULL,
    "region" VARCHAR(255)   NOT NULL,
    "country" VARCHAR(255)   NOT NULL,
    "latitude" FLOAT   NOT NULL,
    "longitude" FLOAT   NOT NULL,
    CONSTRAINT "pk_exchanges" PRIMARY KEY (
        "exchange_id"
     ),
    CONSTRAINT "uc_exchanges_name" UNIQUE (
        "name"
    )
);

CREATE TABLE "investments" (
    "investment_id" SERIAL   NOT NULL,
    "asset_id" INT   NOT NULL,
    "exchange_id" INT   NOT NULL,
    "open_price" FLOAT   NOT NULL,
    "open_timestamp" TIMESTAMP   NOT NULL,
    "close_price" FLOAT   NOT NULL,
    "close_timestamp" TIMESTAMP   NOT NULL,
    CONSTRAINT "pk_investments" PRIMARY KEY (
        "investment_id"
     )
);

CREATE TABLE "portfolios" (
    "portfolio_id" SERIAL   NOT NULL,
    "name" VARCHAR(255)   NOT NULL,
    "investment_period" INT   NOT NULL,
    CONSTRAINT "pk_portfolios" PRIMARY KEY (
        "portfolio_id"
     ),
    CONSTRAINT "uc_portfolios_name" UNIQUE (
        "name"
    )
);

CREATE TABLE "assets_portfolios" (
    "portfolio_id" INT   NOT NULL,
    "asset_id" INT   NOT NULL,
    "weight" FLOAT   NOT NULL
);

ALTER TABLE "exchange_connections" ADD CONSTRAINT "fk_exchange_connections_exchange_id" FOREIGN KEY("exchange_id")
REFERENCES "exchanges" ("exchange_id");

ALTER TABLE "investments" ADD CONSTRAINT "fk_investments_asset_id" FOREIGN KEY("asset_id")
REFERENCES "assets" ("asset_id");

ALTER TABLE "investments" ADD CONSTRAINT "fk_investments_exchange_id" FOREIGN KEY("exchange_id")
REFERENCES "exchanges" ("exchange_id");

ALTER TABLE "assets_portfolios" ADD CONSTRAINT "fk_assets_portfolios_portfolio_id" FOREIGN KEY("portfolio_id")
REFERENCES "portfolios" ("portfolio_id");

ALTER TABLE "assets_portfolios" ADD CONSTRAINT "fk_assets_portfolios_asset_id" FOREIGN KEY("asset_id")
REFERENCES "assets" ("asset_id");

