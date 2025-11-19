--
-- PostgreSQL database dump
--
-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2025-11-19 17:48:24

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16857)
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    phone character varying(20),
    address text,
    city character varying(100),
    postal_code character varying(10),
    state character varying(50),
    country character varying(100) DEFAULT 'Italy'::character varying,
    active boolean DEFAULT true,
    email_verified boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16856)
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_id_seq OWNER TO postgres;

--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 219
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- TOC entry 226 (class 1259 OID 16946)
-- Name: order_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_details (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    subtotal numeric(10,2) NOT NULL,
    CONSTRAINT order_details_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT order_details_subtotal_check CHECK ((subtotal >= (0)::numeric)),
    CONSTRAINT order_details_unit_price_check CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.order_details OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16945)
-- Name: order_details_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_details_id_seq OWNER TO postgres;

--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 225
-- Name: order_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_details_id_seq OWNED BY public.order_details.id;


--
-- TOC entry 224 (class 1259 OID 16905)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    client_id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    total numeric(10,2) NOT NULL,
    subtotal numeric(10,2) NOT NULL,
    shipping_cost numeric(10,2) DEFAULT 0.00,
    tax numeric(10,2) DEFAULT 0.00,
    discount numeric(10,2) DEFAULT 0.00,
    discount_code character varying(50),
    shipping_address text NOT NULL,
    shipping_city character varying(100),
    shipping_postal_code character varying(10),
    shipping_state character varying(50),
    shipping_country character varying(100) DEFAULT 'Italy'::character varying,
    notes text,
    payment_intent_id character varying(255),
    paid boolean DEFAULT false,
    paid_at timestamp without time zone,
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_discount_check CHECK ((discount >= (0)::numeric)),
    CONSTRAINT orders_shipping_cost_check CHECK ((shipping_cost >= (0)::numeric)),
    CONSTRAINT orders_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'paid'::character varying, 'processing'::character varying, 'shipped'::character varying, 'delivered'::character varying, 'cancelled'::character varying, 'refunded'::character varying])::text[]))),
    CONSTRAINT orders_subtotal_check CHECK ((subtotal >= (0)::numeric)),
    CONSTRAINT orders_tax_check CHECK ((tax >= (0)::numeric)),
    CONSTRAINT orders_total_check CHECK ((total >= (0)::numeric))
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16904)
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- TOC entry 5094 (class 0 OID 0)
-- Dependencies: 223
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- TOC entry 222 (class 1259 OID 16880)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    available_quantity integer DEFAULT 0 NOT NULL,
    image_url character varying(500),
    sku character varying(100),
    active boolean DEFAULT true,
    featured boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_available_quantity_check CHECK ((available_quantity >= 0)),
    CONSTRAINT products_price_check CHECK ((price >= (0)::numeric))
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16879)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 5095 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 4871 (class 2604 OID 16860)
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- TOC entry 4892 (class 2604 OID 16949)
-- Name: order_details id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_details ALTER COLUMN id SET DEFAULT nextval('public.order_details_id_seq'::regclass);


--
-- TOC entry 4883 (class 2604 OID 16908)
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- TOC entry 4877 (class 2604 OID 16883)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 5080 (class 0 OID 16857)
-- Dependencies: 220
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clients (id, email, password_hash, first_name, last_name, phone, address, city, postal_code, state, country, active, email_verified, created_at, updated_at) FROM stdin;
1	mario.rossi@email.com	$2b$12$hash1	Mario	Rossi	+39 333 1234567	Via Roma 1	Rome	00100	\N	Italy	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
2	luigi.verdi@email.com	$2b$12$hash2	Luigi	Verdi	+39 333 9876543	Via Milano 5	Milan	20100	\N	Italy	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
3	anna.bianchi@email.com	$2b$12$hash3	Anna	Bianchi	+39 333 5556677	Via Napoli 10	Naples	80100	\N	Italy	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
\.


--
-- TOC entry 5086 (class 0 OID 16946)
-- Dependencies: 226
-- Data for Name: order_details; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_details (id, order_id, product_id, quantity, unit_price, subtotal) FROM stdin;
1	1	1	2	29.99	59.98
2	1	2	1	59.99	59.99
3	2	3	1	89.99	89.99
4	3	1	1	29.99	29.99
5	3	4	1	39.99	39.99
6	4	4	1	39.99	39.99
\.


--
-- TOC entry 5084 (class 0 OID 16905)
-- Dependencies: 224
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, client_id, order_number, status, total, subtotal, shipping_cost, tax, discount, discount_code, shipping_address, shipping_city, shipping_postal_code, shipping_state, shipping_country, notes, payment_intent_id, paid, paid_at, shipped_at, delivered_at, created_at, updated_at) FROM stdin;
1	1	ORD-2024-001	delivered	124.98	119.98	5.00	0.00	0.00	\N	Via Roma 1	Rome	00100	\N	Italy	\N	\N	t	2024-11-10 14:30:00	\N	\N	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
2	1	ORD-2024-002	shipped	89.99	89.99	0.00	0.00	0.00	\N	Via Roma 1	Rome	00100	\N	Italy	\N	\N	t	2024-11-15 10:20:00	\N	\N	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
3	2	ORD-2024-003	paid	69.98	59.98	10.00	0.00	0.00	\N	Via Milano 5	Milan	20100	\N	Italy	\N	\N	t	2024-11-17 09:15:00	\N	\N	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
4	3	ORD-2024-004	pending	44.99	39.99	5.00	0.00	0.00	\N	Via Napoli 10	Naples	80100	\N	Italy	\N	\N	f	\N	\N	\N	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
\.


--
-- TOC entry 5082 (class 0 OID 16880)
-- Dependencies: 222
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, name, description, price, available_quantity, image_url, sku, active, featured, created_at, updated_at) FROM stdin;
1	Red T-Shirt	100% cotton t-shirt	29.99	100	\N	TEE-RED-001	t	t	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
2	Blue Jeans	Slim fit jeans	59.99	50	\N	JEA-BLU-001	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
3	Nike Shoes	Running shoes	89.99	30	\N	SHO-NIKE-001	t	t	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
4	Gray Hoodie	Hoodie with hood	39.99	75	\N	HOO-GRAY-001	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
5	Black Jacket	Waterproof jacket	79.99	20	\N	JAC-BLK-001	t	f	2025-11-19 17:38:56.694053	2025-11-19 17:38:56.694053
\.


--
-- TOC entry 5096 (class 0 OID 0)
-- Dependencies: 219
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clients_id_seq', 3, true);


--
-- TOC entry 5097 (class 0 OID 0)
-- Dependencies: 225
-- Name: order_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_details_id_seq', 6, true);


--
-- TOC entry 5098 (class 0 OID 0)
-- Dependencies: 223
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 4, true);


--
-- TOC entry 5099 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 5, true);


--
-- TOC entry 4905 (class 2606 OID 16876)
-- Name: clients clients_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_email_key UNIQUE (email);


--
-- TOC entry 4907 (class 2606 OID 16874)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4928 (class 2606 OID 16960)
-- Name: order_details order_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT order_details_pkey PRIMARY KEY (id);


--
-- TOC entry 4922 (class 2606 OID 16935)
-- Name: orders orders_order_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_order_number_key UNIQUE (order_number);


--
-- TOC entry 4924 (class 2606 OID 16933)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 4914 (class 2606 OID 16898)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4916 (class 2606 OID 16900)
-- Name: products products_sku_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);


--
-- TOC entry 4908 (class 1259 OID 16877)
-- Name: idx_clients_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_active ON public.clients USING btree (active);


--
-- TOC entry 4909 (class 1259 OID 16878)
-- Name: idx_clients_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_email ON public.clients USING btree (email);


--
-- TOC entry 4925 (class 1259 OID 16971)
-- Name: idx_order_details_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_details_order ON public.order_details USING btree (order_id);


--
-- TOC entry 4926 (class 1259 OID 16972)
-- Name: idx_order_details_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_details_product ON public.order_details USING btree (product_id);


--
-- TOC entry 4917 (class 1259 OID 16941)
-- Name: idx_orders_client; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_client ON public.orders USING btree (client_id);


--
-- TOC entry 4918 (class 1259 OID 16944)
-- Name: idx_orders_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_created ON public.orders USING btree (created_at);


--
-- TOC entry 4919 (class 1259 OID 16943)
-- Name: idx_orders_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_number ON public.orders USING btree (order_number);


--
-- TOC entry 4920 (class 1259 OID 16942)
-- Name: idx_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_status ON public.orders USING btree (status);


--
-- TOC entry 4910 (class 1259 OID 16901)
-- Name: idx_products_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_active ON public.products USING btree (active);


--
-- TOC entry 4911 (class 1259 OID 16902)
-- Name: idx_products_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_name ON public.products USING btree (name);


--
-- TOC entry 4912 (class 1259 OID 16903)
-- Name: idx_products_price; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_price ON public.products USING btree (price);


--
-- TOC entry 4930 (class 2606 OID 16961)
-- Name: order_details order_details_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT order_details_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- TOC entry 4931 (class 2606 OID 16966)
-- Name: order_details order_details_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT order_details_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;


--
-- TOC entry 4929 (class 2606 OID 16936)
-- Name: orders orders_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


-- Completed on 2025-11-19 17:48:25

--
-- PostgreSQL database dump complete
--

