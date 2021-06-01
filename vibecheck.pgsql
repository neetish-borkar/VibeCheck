--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: fingerprints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fingerprints (
    hash bytea NOT NULL,
    s_id integer NOT NULL,
    h_offset integer NOT NULL
);


ALTER TABLE public.fingerprints OWNER TO postgres;

--
-- Name: songs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.songs (
    s_id integer NOT NULL,
    s_name character varying(250) NOT NULL,
    s_artist1 character varying(250) NOT NULL,
    s_artist2 character varying(250),
    s_genre character varying(250)
);


ALTER TABLE public.songs OWNER TO postgres;

--
-- Name: songs_s_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.songs_s_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.songs_s_id_seq OWNER TO postgres;

--
-- Name: songs_s_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.songs_s_id_seq OWNED BY public.songs.s_id;


--
-- Name: songs s_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.songs ALTER COLUMN s_id SET DEFAULT nextval('public.songs_s_id_seq'::regclass);


--
-- Name: songs songs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.songs
    ADD CONSTRAINT songs_pkey PRIMARY KEY (s_id);


--
-- Name: hash_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX hash_index ON public.fingerprints USING btree (hash);


--
-- Name: fingerprints fk_fingerprints_s_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fingerprints
    ADD CONSTRAINT fk_fingerprints_s_id FOREIGN KEY (s_id) REFERENCES public.songs(s_id) ON DELETE CASCADE;


--
-- Name: TABLE fingerprints; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.fingerprints TO neetish;


--
-- Name: TABLE songs; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.songs TO neetish;


--
-- Name: SEQUENCE songs_s_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.songs_s_id_seq TO neetish;


--
-- PostgreSQL database dump complete
--

