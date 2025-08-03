DROP TABLE IF EXISTS region, nation, part, supplier, partsupp, customer, orders, lineitem CASCADE;

CREATE TABLE region (
    r_regionkey INTEGER NOT NULL PRIMARY KEY,
    r_name      CHAR(25),
    r_comment   VARCHAR(152)
);

CREATE TABLE nation (
    n_nationkey INTEGER NOT NULL PRIMARY KEY,
    n_name      CHAR(25),
    n_regionkey INTEGER REFERENCES region(r_regionkey),
    n_comment   VARCHAR(152)
);

CREATE TABLE part (
    p_partkey     INTEGER NOT NULL PRIMARY KEY,
    p_name        VARCHAR(55),
    p_mfgr        CHAR(25),
    p_brand       CHAR(10),
    p_type        VARCHAR(25),
    p_size        INTEGER,
    p_container   CHAR(10),
    p_retailprice DECIMAL(15,2),
    p_comment     VARCHAR(23)
);

CREATE TABLE supplier (
    s_suppkey   INTEGER NOT NULL PRIMARY KEY,
    s_name      CHAR(25),
    s_address   VARCHAR(40),
    s_nationkey INTEGER REFERENCES nation(n_nationkey),
    s_phone     CHAR(15),
    s_acctbal   DECIMAL(15,2),
    s_comment   VARCHAR(101)
);

CREATE TABLE partsupp (
    ps_partkey    INTEGER NOT NULL REFERENCES part(p_partkey),
    ps_suppkey    INTEGER NOT NULL REFERENCES supplier(s_suppkey),
    ps_availqty   INTEGER,
    ps_supplycost DECIMAL(15,2),
    ps_comment    VARCHAR(199),
    PRIMARY KEY (ps_partkey, ps_suppkey)
);

CREATE TABLE customer (
    c_custkey    INTEGER NOT NULL PRIMARY KEY,
    c_name       VARCHAR(25),
    c_address    VARCHAR(40),
    c_nationkey  INTEGER REFERENCES nation(n_nationkey),
    c_phone      CHAR(15),
    c_acctbal    DECIMAL(15,2),
    c_mktsegment CHAR(10),
    c_comment    VARCHAR(117)
);

CREATE TABLE orders (
    o_orderkey      INTEGER NOT NULL PRIMARY KEY,
    o_custkey       INTEGER REFERENCES customer(c_custkey),
    o_orderstatus   CHAR(1),
    o_totalprice    DECIMAL(15,2),
    o_orderdate     DATE,
    o_orderpriority CHAR(15),
    o_clerk         CHAR(15),
    o_shippriority  INTEGER,
    o_comment       VARCHAR(79)
);

CREATE TABLE lineitem (
    l_orderkey      INTEGER NOT NULL REFERENCES orders(o_orderkey),
    l_partkey       INTEGER NOT NULL REFERENCES part(p_partkey),
    l_suppkey       INTEGER NOT NULL REFERENCES supplier(s_suppkey),
    l_linenumber    INTEGER NOT NULL,
    l_quantity      DECIMAL(15,2),
    l_extendedprice DECIMAL(15,2),
    l_discount      DECIMAL(15,2),
    l_tax           DECIMAL(15,2),
    l_returnflag    CHAR(1),
    l_linestatus    CHAR(1),
    l_shipdate      DATE,
    l_commitdate    DATE,
    l_receiptdate   DATE,
    l_shipinstruct  CHAR(25),
    l_shipmode      CHAR(10),
    l_comment       VARCHAR(44),
    PRIMARY KEY (l_orderkey, l_linenumber)
);
